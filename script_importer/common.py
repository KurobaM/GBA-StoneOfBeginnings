# Copyright (C) 2026, KurobaM
# SPDX-License-Identifier: GPL-3.0-or-later

# to treat warning as error and perform 4 bytes align address:
#   python -W error script_name.py    

from __future__ import annotations
import json
from typing import Protocol, Callable
import warnings

# Must change when:
#   json field name change
#   json field 'type' value change
#   data structure change
FORMAT_VERSION = '1.0'


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, GbaAddr):
            return {'value': hex(obj.value), 'type': 'Address'}
        if isinstance(obj, SjisString):
            return {'pointer address': obj.p_addr, 'address': obj.addr,
                    'new address': obj.n_addr, 'length': obj.length,
                    'raw': obj.orig, 'translation': obj.trans,
                    'type': 'SJIS string'}
        return super().default(obj)


def decoder(data):
    if 'type' in data and data['type'] == 'Address':
        return GbaAddr(int(data['value'], 16))
    if 'type' in data and data['type'] == 'SJIS string':
        return SjisString(data['pointer address'], data['address'],
                          data['length'], data['raw'],
                          data['new address'], data['translation'])
    return data


def save_json(obj, file_name):
    out = json.dumps(obj, cls=Encoder, indent=4,
                     ensure_ascii=False, sort_keys=True)
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(out)
        f.write('\n')

        
def load_json(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        data = f.read()
    return json.loads(data, object_hook=decoder)
    

class GbaAddr:
    def __init__(self, value: int):
        if value > 0x0fffffff:
            raise ValueError('Invalid address. Only 28bit address allowed.')
        try:
            if value & 0x3:
                warnings.warn('Address is not 4 bytes aligned.')
            self.value = value
        except UserWarning:
            warnings.warn('Address is not 4 bytes aligned. '
                          'Convert to 4 bytes aligned address.')
            self.value = value & 0x0ffffffc
        
    def __repr__(self):
        return f"{hex(self.value)}"


class SjisString:
    def __init__(self, pointer_addr: list[GbaAddr], address: GbaAddr | None = None,
                 length: int = 0, original: str = '',
                 new_addr: GbaAddr | None = None, translation: str = ''):
        self.p_addr = pointer_addr
        self.addr = address
        self.length = length
        self.orig = original
        self.n_addr = new_addr
        self.trans = translation
        
    def __repr__(self):
        txt = self.orig.rstrip('\x00')
        return f'SJIS({self.addr}, {self.p_addr}, {self.length}, {txt})'
        
    @classmethod
    def from_addr(cls, pointer_addr: list[int],
                  reader: Callable[[int, int, ...], bytes], length: int = 0):
        if not pointer_addr:
            raise ValueError('Must have at least 1 pointer address.')
        pa = [GbaAddr(x) for x in pointer_addr]
        a = GbaAddr(int.from_bytes(reader(pa[0].value, 4), 'little'))
        if length > 0:
            l = length
            o = reader(a.value, l).decode('sjis')
        else:
            chunk_size = 32
            addr = a.value
            buffer = reader(addr, chunk_size)
            while b'\x00\x00' not in buffer:
                addr += chunk_size
                buffer += reader(addr, chunk_size)
            idx = buffer.index(b'\x00\x00')
            # alignment
            if len(buffer[idx:]) < 4:
                buffer += reader(addr, 4 - len(buffer[idx:]))
            if buffer[idx:][2] != 0:
                buffer = buffer[:idx+2]
            else:
                if buffer[idx:][3] != 0:
                    buffer = buffer[:idx+3]
                else:
                    buffer = buffer[:idx+4]
            l = len(buffer)
            o = buffer.decode('sjis')
        return cls(pa, a, l, o, None, '')
