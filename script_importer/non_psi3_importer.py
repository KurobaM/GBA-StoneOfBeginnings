# Copyright (C) 2026, KurobaM
# SPDX-License-Identifier: GPL-3.0-or-later

# to treat warning as error and perform 4 bytes align address:
#   python -W error non_psi3.py

from __future__ import annotations
import hashlib
import os
import json
import sys

from common import (GbaAddr, load_json, StructArray,
                    SjisString as String, SjisStrTable as Table)


def clear_region_code(sjis: String):
    txt = json.dumps(sjis.orig, ensure_ascii=False)
    if sjis.length == 0:
        return f'; str={txt}\n'
    return (
        f'; str={txt}\n'
        f'.org {hex(sjis.addr.value)}\n'
        f'.region {hex(sjis.addr.value + sjis.length)}-., 0x00\n'
        '.endregion\n')


def debug_code(sjis: String, index: int):
    if index > 0xffff:
        raise NotImplementedError('Too many strings')
    if sjis.length < 4:
        return f'; index={index} str={sjis.orig}\n'
    if sjis.length == 4:
        code = f'.dw {hex(0x958d | (index & 0xffff) << 16)}'
    else:
        buffer = b'968' + int.to_bytes(index & 0xffff, 2, 'little')
        code = '.db ' + ', '.join([f'0x{c:02x}' for c in buffer])
    return (
        f'; index={index} str={json.dumps(sjis.orig, ensure_ascii=False)}\n'
        f'.org {hex(sjis.addr.value)}\n'
        f'{code}\n'
    )


def is_null(buffer: bytes):
    null = True
    for x in buffer:
        if x > 0:
            null = False
            break
    return null


def sjis_to_bytes(s: str, max: int = 0):
    data = s.encode('cp932')
    if not max:
        return data + b'\x00' * (len(data) % 2)
    out = data + b'\x00' * (max - len(data))
    if b'"' in out and len(out) > 4:
        return out[: max - 2] + b'\x00\x00'
    else:
        return out[: max - 1] + b'\x00'


def generate_struct_code(sa: StructArray):
    out = [f'; structarray 0x{sa.addr.value:x}',]
    for s in sa.content:
        for sm in s.content:
            max = sm.size
            buffer = sjis_to_bytes(sm.data.trans)
            if buffer[-2] != 0 and len(buffer) + 2 <= max:
                buffer = buffer + b'\x00\x00'
            code = ', '.join([f'0x{c:02x}' for c in buffer])
            out.append(
                f'; txt={json.dumps(sm.data.trans, ensure_ascii=False)}\n'
                f'.org {hex(sm.data.addr.value)}\n'
                f'.area {hex(sm.data.addr.value + len(buffer))}-., 0x00\n'
                f'.db {code}\n'
                '.endarea\n'
                f'.org {hex(sm.data.addr.value + len(buffer))}\n'
                f'.region {hex(sm.data.addr.value + max)}-., 0x00\n'
                '.endregion\n')
    return out


def generate_auto_region_code(sjis: String, index: int):
    if not sjis.trans:
        return ''
    buffer = sjis_to_bytes(sjis.trans)
    if is_null(buffer):
        return ''
    code = ', '.join([f'0x{c:02x}' for c in buffer])
    return (
        f'; index={index}, txt={json.dumps(sjis.trans, ensure_ascii=False)}\n'
        f'.autoregion\n'
        f'auto_txt_{index}:\n'
        f'.db {code}\n'
        '.align 4\n'
        '.endautoregion\n')


def generate_addr_code(addr: GbaAddr, s: String,
                       p_addr: list[GbaAddr] | None = None):
    out: list[str] = []
    if p_addr is not None:
        p = p_addr
    else:
        p = s.p_addr
    if (addr.value > 0 and addr.value < 0x8000000) or p is None:
        print(f'Skip: str({s.p_addr}, {s.addr}, {s.orig})')
    else:
        for a in p:
            out.append(f'.org {hex(a.value)}\n'
                       f'.dw {hex(addr.value)}\n')
    return out


def generate_auto_addr_code(s: String, index: int,
                            p_addr: list[GbaAddr] | None = None):
    out: list[str] = []
    if p_addr is not None:
        p = p_addr
    else:
        p = s.p_addr
    if p is None:
        print(f'Skip: str({s.p_addr}, {s.addr}, {s.orig})')
    else:
        for a in p:
            out.append(f'.org {hex(a.value)}\n'
                       f'.dw org(auto_txt_{index})\n')
    return out


def generate_str_code(map: dict[str, int], addr_map: dict[int, GbaAddr | None],
                      s: String, p_addr: list[GbaAddr] | None = None,
                      in_table: bool = False):
    out: list[str] = []
    if not s.trans:
        return out
    if not in_table:
        p_addr = None
        if s.p_addr is None:
            print(f'Skip: str({s.p_addr}, {s.addr}, {s.orig})')
            return out
    if (in_table and s.addr.value == 0 and p_addr and s.p_addr
            and p_addr[0].value != s.p_addr[0].value):
        out.extend(generate_addr_code(s.addr, s, p_addr))
        return out

    index = map[s.trans]
    addr = addr_map[index]
    if addr is not None:
        if addr.value == 0:
            out.extend(generate_auto_addr_code(s, index, p_addr))
        else:
            out.extend(generate_addr_code(addr, s, p_addr))
        return out

    out.append(clear_region_code(s))
    code = generate_auto_region_code(s, index)
    out.append(code)
    if '.autoregion' in code:
        out.extend(generate_auto_addr_code(s, index, p_addr))
        addr_map[index] = GbaAddr(0)
    return out


if __name__ == '__main__':
    path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', 'script/non_psi3', 'data.json'))
    out_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', 'asm/non_psi3_script_text.asm'))
    config_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'non_psi3_config.json'))
    if not os.path.isfile(path):
        sys.exit()
    config = dict()
    with open(path, 'rb') as f:
        raw = f.read()
    config[path] = hashlib.sha256(raw).hexdigest()

    if not os.path.isfile(config_path):
        with open(config_path, 'w') as f:
            json.dump(config, f)
    else:
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        if config_data[path] == config[path]:
            sys.exit()

    data: dict[str, String | Table | StructArray | str] = load_json(path)
    data.pop('__version__')

    out = ['; This file content is auto-generated\n']
    string: list[String] = []
    table: list[Table] = []

    for v in data.values():
        if isinstance(v, StructArray):
            out.extend(generate_struct_code(v))
        elif isinstance(v, Table):
            table.append(v)
        elif isinstance(v, String):
            string.append(v)

    map: dict[str, int] = dict()
    addr_map: dict[int, GbaAddr | None] = dict()
    index = 0

    for s in string:
        if not s.trans:
            continue
        if s.trans not in map:
            map[s.trans] = index
            addr_map[index] = None
            index += 1

    for t in table:
        for s in t.content:
            if not s.trans:
                continue
            if s.trans not in map:
                map[s.trans] = index
                addr_map[index] = None
                index += 1

    for s in string:
        out.extend(generate_str_code(map, addr_map, s))

    for t in table:
        base_addr = t.n_addr if (
            t.n_addr is not None and t.n_addr.value > 0x8000000) else t.addr
        if base_addr.value < 0x8000000:
            print(f'Skip: table({t.p_addr}, {t.addr}, {t.length})')
        for i, s in enumerate(t.content):
            p_addr = GbaAddr(base_addr.value + i * 4)
            out.extend(generate_str_code(map, addr_map, s, [p_addr], True))

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))
    print(f'Write non-psi3 script text to {out_path}')

    with open(config_path, 'w') as f:
        json.dump(config, f)
