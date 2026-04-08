# Copyright (C) 2026, KurobaM
# SPDX-License-Identifier: GPL-3.0-or-later


from __future__ import annotations
from dataclasses import dataclass
import json
from typing import Any, Callable
import warnings


FORMAT_VERSION = '1.0'


class Encoder(json.JSONEncoder):
    def default(self, obj) -> dict[str, Any]:   # type: ignore
        if isinstance(obj, GbaAddr):
            return {'value': hex(obj.value), 'type': 'Address'}
        if isinstance(obj, SjisString):
            return {'pointer address': obj.p_addr, 'address': obj.addr,
                    'new address': obj.n_addr, 'length': obj.length,
                    'raw': obj.orig, 'translation': obj.trans,
                    'type': 'SJIS string'}
        if isinstance(obj, SjisStrTable):
            return {'pointer address': obj.p_addr, 'address': obj.addr,
                    'new address': obj.n_addr, 'data': obj.content,
                    'type': 'SJIS table'}
        if isinstance(obj, SjisStructMember):
            return {'offset': obj.offset, 'size': obj.size,
                    'data': obj.data, 'type': 'StructMember'}
        if isinstance(obj, Struct):
            return {'pointer address': obj.p_addr, 'address': obj.addr,
                    'new address': obj.n_addr, 'data': obj.content,
                    'size': obj.size, 'type': 'Struct'}
        if isinstance(obj, StructArray):
            return {'pointer address': obj.p_addr, 'address': obj.addr,
                    'new address': obj.n_addr, 'data': obj.content,
                    'type': 'StructArray'}
        return super().default(obj)


def decoder(data) -> object:
    if 'type' in data and data['type'] == 'Address':
        return GbaAddr(int(data['value'], 16))
    if 'type' in data and data['type'] == 'SJIS string':
        return SjisString(data['pointer address'], data['address'],
                          data['length'], data['raw'],
                          data['new address'], data['translation'])
    if 'type' in data and data['type'] == 'SJIS table':
        return SjisStrTable(data['pointer address'], data['address'],
                            data['data'], data['new address'])
    if 'type' in data and data['type'] == 'StructMember':
        return SjisStructMember(data['offset'], data['size'],
                                data['data'])
    if 'type' in data and data['type'] == 'Struct':
        return Struct(data['pointer address'], data['address'], data['size'],
                      data['data'], data['new address'])
    if 'type' in data and data['type'] == 'StructArray':
        return StructArray(data['pointer address'], data['address'],
                           data['data'], data['new address'])
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

    def is_not_word_align(self):
        return bool(self.value & 0x3)

    def __str__(self):
        return hex(self.value)

    def __repr__(self):
        return hex(self.value)

    def __eq__(self, value: object) -> bool:
        return isinstance(value, GbaAddr) and self.value == value.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __ne__(self, value: object) -> bool:
        return not self.__eq__(value)

    def __lt__(self, other: GbaAddr):
        return self.value < other.value

    def __le__(self, other: GbaAddr):
        return self.value < other.value

    def __gt__(self, other: GbaAddr):
        return self.value > other.value

    def __ge__(self, other: GbaAddr):
        return self.value >= other.value


class SjisStrTable:
    def __init__(
            self, pointer_addr: list[GbaAddr], address: GbaAddr,
            table: list[SjisString] = [], new_addr: GbaAddr | None = None):
        self.p_addr = pointer_addr
        self.addr = address
        self.length = len(table)
        self.content = table
        self.n_addr = new_addr

    def __repr__(self):
        return f'String {self.addr} [{self.length}]'

    @classmethod
    def from_addr(cls, pointer_addr: list[int],
                  reader: Callable[[int, int], bytes], length: int = 0):
        if not pointer_addr:
            raise ValueError('Must have at least 1 pointer address.')
        t_pa = [GbaAddr(x) for x in pointer_addr]
        t_a = GbaAddr(int.from_bytes(reader(t_pa[0].value, 4), 'little'))
        if length <= 0:
            raise ValueError('Must have at least 1 string.')
        content = []
        for i in range(0, length):
            content.append(SjisString.from_addr([t_a.value + i * 4], reader))
        return cls(t_pa, t_a, content, None)


@dataclass
class SjisStructMember:
    offset: int
    size: int
    data: SjisString


class StructArray:
    def __init__(self, pointer_addr: list[GbaAddr],
                 address: GbaAddr, data: list[Struct],
                 new_addr: GbaAddr | None = None) -> None:
        self.p_addr = pointer_addr
        self.addr = address
        self.count = len(data)
        self.content = data
        self.n_addr = new_addr

    def __repr__(self):
        return f'Struct {self.addr} [{self.count}]'

    @classmethod
    def from_addr(cls, pointer_addr: list[int],
                  reader: Callable[[int, int], bytes], count: int, size: int,
                  sjis: list[tuple[int, int]]):
        if not pointer_addr:
            raise ValueError('Must have either ptr address or address.')
        s_pa = [GbaAddr(x) for x in pointer_addr]
        s_a = GbaAddr(int.from_bytes(reader(s_pa[0].value, 4), 'little'))
        if count <= 0:
            raise ValueError()
        data = []
        for i in range(0, count):
            pa = None
            a = s_a.value + size * i
            data.append(Struct.from_addr(pa, reader, size, sjis, a))
        return cls(s_pa, s_a, data, None)


class Struct:
    def __init__(
            self, pointer_addr: list[GbaAddr] | None,
            address: GbaAddr, size: int, sjis: list[SjisStructMember] = [],
            new_addr: GbaAddr | None = None):
        self.p_addr = pointer_addr
        self.addr = address
        self.size = size
        self.content = sjis
        self.n_addr = new_addr

    def __repr__(self):
        return f'Struct({self.addr}, size={self.size})'

    @classmethod
    def from_addr(cls, pointer_addr: list[int] | None,
                  reader: Callable[[int, int], bytes], size: int,
                  sjis: list[tuple[int, int]],
                  address: int | None = None,):
        if not pointer_addr:
            if not address:
                raise ValueError('Must have either ptr address or address.')
            pa = None
            a = GbaAddr(address)
        else:
            pa = [GbaAddr(x) for x in pointer_addr]
            a = GbaAddr(int.from_bytes(reader(pa[0].value, 4), 'little'))
        if size <= 0:
            raise ValueError()
        content = []
        for offset, strlen in sjis:
            if offset + strlen > size:
                raise ValueError()
            member = SjisStructMember(
                offset, strlen,
                SjisString.from_addr(None, reader, a.value + offset, strlen))
            content.append(member)
        return cls(pa, a, size, content, None)


class SjisString:
    def __init__(self, pointer_addr: list[GbaAddr] | None, address: GbaAddr,
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
        return f'String ({self.addr}, {self.length}, {txt})'

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, SjisString):
            return False
        if self.addr != value.addr:
            return False
        if self.length != value.length:
            return False
        return True

    def merge(self, other: SjisString):
        if self.__eq__(other):
            if self.p_addr is not None:
                if other.p_addr is not None:
                    self.p_addr = sorted(list(set(self.p_addr + other.p_addr)))
            else:
                if other.p_addr is not None:
                    self.p_addr = other.p_addr

    @classmethod
    def from_addr(cls, pointer_addr: list[int] | None,
                  reader: Callable[[int, int], bytes],
                  address: int | None = None, length: int = 0):
        if not pointer_addr:
            if not address:
                raise ValueError('Must have either ptr address or address.')
            pa = None
            a = GbaAddr(address)
        else:
            pa = [GbaAddr(x) for x in pointer_addr]
            a = GbaAddr(int.from_bytes(reader(pa[0].value, 4), 'little'))
        if a.value < 0x8000000:
            return cls(pa, a, 0, '', None, '')
        if length > 0:
            strlen = length
            o = reader(a.value, strlen).decode('cp932')
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
            strlen = len(buffer)
            o = buffer.decode('cp932')
        return cls(pa, a, strlen, o, None, '')
