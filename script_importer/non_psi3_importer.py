# Copyright (C) 2026, KurobaM
# SPDX-License-Identifier: GPL-3.0-or-later

# to treat warning as error and perform 4 bytes align address:
#   python -W error non_psi3.py

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import hashlib
import os
import json
import sys
from tkinter import Tk, messagebox

from common import (GbaAddr, load_json, StructArray,
                    SjisString as String, SjisStrTable as Table)


def clear_region_code(sjis: String):
    txt = json.dumps(sjis.orig, ensure_ascii=False)
    if sjis.length == 0:
        return f''
    return (
        f'; str={txt}\n'
        f'.org {hex(sjis.addr.value)}\n'
        f'.region {hex(sjis.addr.value + sjis.length)}-., 0x00\n'
        '.endregion\n')


def debug_code(sjis: String, index: int | None):
    if index is not None and index >= 0x7f00:
        raise NotImplementedError('Too many strings')
    if index is None:
        index = 0x7f30
    if sjis.length == 0:
        return ''
    if sjis.length < 4:
        code = f'.dh 0x45'
    elif sjis.length == 4:
        code = f'.dw {hex(0x45 | (index & 0xffff) << 8)}'
    else:
        code = f'.dw {hex(0xeb8c | (index & 0xffff) << 16)}\n.db 0x00, 0x00'
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
    for ti, s in enumerate(sa.content):
        for sm in s.content:
            max = sm.size
            buffer = sjis_to_bytes(sm.data.trans)
            if buffer[-2] != 0 and len(buffer) + 2 <= max:
                buffer = buffer + b'\x00\x00'
            code = ', '.join([f'0x{c:02x}' for c in buffer])
            txt = json.dumps(sm.data.trans, ensure_ascii=False)
            if is_null(buffer):
                out.append(
                    f'; txt={txt}\n'
                    f'.org {sm.data.addr}\n'
                    f'.area {hex(sm.data.addr.value + 2)}-., 0x00\n'
                    f'.db 0x00, 0x00\n'
                    '.endarea\n'
                    f'.org {hex(sm.data.addr.value + 2)}\n'
                    f'.region {hex(sm.data.addr.value + max)}-., 0x00\n'
                    '.endregion\n')
            elif len(buffer) <= max:
                out.append(
                    f'; txt={txt}\n'
                    f'.org {hex(sm.data.addr.value)}\n'
                    f'.area {hex(sm.data.addr.value + len(buffer))}-., 0x00\n'
                    f'.db {code}\n'
                    '.endarea\n'
                    f'.org {hex(sm.data.addr.value + len(buffer))}\n'
                    f'.region {hex(sm.data.addr.value + max)}-., 0x00\n'
                    '.endregion\n')
            else:
                out.append(
                    f'; OVERFLOW txt={txt}\n'
                    f'; notice "StructArray {sa.addr} content at index={ti} '
                    f'offset={sm.offset} OVERFLOW"\n')
    return out


def generate_auto_region_code(sjis: String, index: int):
    out = [
        f'; index={index}, txt={json.dumps(sjis.trans, ensure_ascii=False)}\n']
    buffer = sjis_to_bytes(sjis.trans)
    code = ', '.join([f'0x{c:02x}' for c in buffer])
    out.append(
        f'.autoregion\n'
        f'auto_txt_{index}:\n'
        f'.db {code}\n'
        '.align 4\n'
        '.endautoregion\n')
    return '\n'.join(out)


def generate_auto_addr_code(info: ImportInfo):
    out: list[str] = []
    p_addr = []
    if info.ref:
        t = info.ref[0]
        if t.n_addr:
            if t.n_addr.value < 0x8000000 or t.n_addr.is_not_word_align():
                print(f'ERROR: invalid new address "{t.n_addr}" of {t}')
                return out
            for tpa in t.p_addr:
                out.append(f'; {t}\n.org {tpa}\n.dw {t.n_addr}\n')
        base = t.n_addr if t.n_addr else t.addr
        p_addr = [GbaAddr(base.value + info.ref[1] * 4)]
    else:
        if info.data.p_addr:
            p_addr = info.data.p_addr
    for pa in p_addr:
        if pa.value < 0x8000000 or pa.is_not_word_align():
            print(f'ERROR: invalid ptr address "{pa}" of {info.data}')
        else:
            out.append(f'.org {pa}\n.dw org(auto_txt_{info.index})\n')
    return out


def generate_area_code(sjis: String, index: int, addr: GbaAddr):
    out = [
        f'; index={index}, txt={json.dumps(sjis.trans, ensure_ascii=False)}\n']
    buffer = sjis_to_bytes(sjis.trans)
    code = ', '.join([f'0x{c:02x}' for c in buffer])
    out.append(
        f'.org {addr}\n'
        f'area {hex(addr.value + len(buffer))}-., 0x00\n'
        f'.db {code}\n'
        '.endarea\n')
    return '\n'.join(out)


def generate_overwrite_code(info: ImportInfo, free: bool = False):
    sjis = info.data
    index = info.index
    addr = info.new_addr if info.new_addr else sjis.addr
    out = [
        f'; index={index}, txt={json.dumps(sjis.trans, ensure_ascii=False)}\n']
    buffer = sjis_to_bytes(sjis.trans)
    code = ', '.join([f'0x{c:02x}' for c in buffer])
    if len(buffer) > sjis.length:
        raise ValueError(f'Overwrite error: {sjis}')
    out.append(
        f'.org {addr}\n'
        f'.db {code}\n')
    if len(buffer) < sjis.length and free:
        out.append(
            f'.org {hex(addr.value + len(buffer))}\n'
            f'.region {hex(addr.value + sjis.length)}-., 0x00\n'
            '.endregion\n')
    return '\n'.join(out)


def generate_addr_code(info: ImportInfo, addr: GbaAddr):
    out: list[str] = []
    p_addr = []

    if addr.value < 0x8000000:
        print(f'ERROR: invalid new address "{addr}" of {info.data}')
        return out
    if info.ref:
        t = info.ref[0]
        if t.n_addr:
            if t.n_addr.value < 0x8000000 or t.n_addr.is_not_word_align():
                print(f'ERROR: invalid new address "{t.n_addr}" of {t}')
                return out
            for tpa in t.p_addr:
                out.append(f'; {t}\n.org {tpa}\n.dw {t.n_addr}\n')
        base = t.n_addr if t.n_addr else t.addr
        p_addr = [GbaAddr(base.value + info.ref[1] * 4)]
    else:
        if info.data.p_addr:
            p_addr = info.data.p_addr
    for pa in p_addr:
        if pa.value < 0x8000000 or pa.is_not_word_align():
            print(f'ERROR: invalid ptr address "{pa}" of {info.data}')
        else:
            out.append(f'.org {pa}\n.dw {addr}\n')
    return out


def max_count(count: dict[tuple[int, Type], int]):
    tmp_o = []
    tmp_o_d = dict()
    tmp_r = []
    tmp_r_d = dict()
    for k, cnt in count.items():
        addr, itype = k
        if itype is Type.OVERWRITE:
            tmp_o.append(cnt)
            tmp_o_d[cnt] = addr
        elif itype is Type.RELOC:
            tmp_r.append(cnt)
            tmp_r_d[cnt] = addr
    if tmp_o:
        return GbaAddr(tmp_o_d[max(tmp_o)]), Type.OVERWRITE
    if tmp_r:
        return GbaAddr(tmp_r_d[max(tmp_r)]), Type.RELOC
    raise ValueError()


class InfoEncoder(json.JSONEncoder):
    def default(self, obj) -> object:    # type: ignore
        if isinstance(obj, GbaAddr):
            return {'addr': str(obj)}
        if isinstance(obj, Type):
            return obj.name
        if isinstance(obj, ImportInfo):
            return {'data': str(obj.data),
                    'ref': ('None' if obj.ref is None
                            else f'{obj.ref[0]} idx={obj.ref[1]}'),
                    'type': obj.type}
        return super().default(obj)


class Type(Enum):
    TBD = 0
    CLEAR = 1
    OVERWRITE = 2
    RELOC = 3
    NULL = 4


@dataclass
class ImportInfo:
    data: String
    ref: tuple[Table, int] | None
    type: Type
    index: int | None
    new_addr: GbaAddr | None = None


def main():
    dir = os.path.join(os.path.dirname(__file__), '..')
    path = os.path.abspath(os.path.join(dir, 'script/non_psi3', 'data.json'))
    text_path = os.path.abspath(
        os.path.join(dir, 'asm/non_psi3_script_text.asm'))
    struc_path = os.path.abspath(
        os.path.join(dir, 'asm/non_psi3_script_text_struc.asm'))
    config_path = os.path.abspath(
        os.path.join(dir, 'script_importer/non_psi3_config.json'))
    debug_path = os.path.abspath(
        os.path.join(dir, 'script_importer/non_psi3_debug.json'))
    if not os.path.isfile(path):
        sys.exit()
    config = dict()
    with open(path, 'rb') as f:
        raw = f.read()
    config[path] = hashlib.sha256(raw).hexdigest()

    if os.path.isfile(config_path):
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        if config_data[path] == config[path]:
            root = Tk()
            root.withdraw()
            a = messagebox.askyesno(
                '', 'data.json has not changed. Continue? Y/N:')
            root.destroy()
            if not a:
                sys.exit()

    data: dict[str, String | Table | StructArray | str] = load_json(path)
    data.pop('__version__')

    out = ['; This file content is auto-generated\n']
    struc = ['; This file content is auto-generated\n']
    string: list[String] = []
    table: list[Table] = []

    for v in data.values():
        if isinstance(v, StructArray):
            struc.extend(generate_struct_code(v))
        elif isinstance(v, Table):
            table.append(v)
        elif isinstance(v, String):
            string.append(v)

    str_map: dict[bytes, int] = dict()
    idx_map: dict[int, list[ImportInfo]] = dict()
    addr_map: dict[int, GbaAddr | None] = dict()

    index = 0
    clear: list[ImportInfo] = []
    null: list[ImportInfo] = []

    have_null = False

    for s in string:
        if s.length == 0:
            continue
        if not s.trans:
            clear.append(ImportInfo(s, None, Type.CLEAR, None))
            continue
        buffer = sjis_to_bytes(s.trans)
        if is_null(buffer):
            have_null = True
            null.append(ImportInfo(s, None, Type.NULL, None))
            continue
        if buffer not in str_map:
            str_map[buffer] = index
            addr_map[index] = None
            idx_map[index] = []
            index += 1
        idx = str_map[buffer]
        if len(buffer) > s.length:
            idx_map[idx].append(ImportInfo(s, None, Type.RELOC, idx))
        else:
            idx_map[idx].append(ImportInfo(s, None, Type.OVERWRITE, idx))

    for t in table:
        for i, s in enumerate(t.content):
            if s.length == 0:
                continue
            if not s.trans:
                clear.append(ImportInfo(s, (t, i), Type.CLEAR, None))
                continue
            buffer = sjis_to_bytes(s.trans)
            if is_null(buffer):
                have_null = True
                null.append(ImportInfo(s, None, Type.NULL, None))
                continue
            if s.trans not in str_map:
                str_map[buffer] = index
                addr_map[index] = None
                idx_map[index] = []
                index += 1
            idx = str_map[buffer]
            if len(buffer) > s.length:
                idx_map[idx].append(ImportInfo(s, (t, i), Type.RELOC, idx))
            else:
                idx_map[idx].append(ImportInfo(s, (t, i), Type.OVERWRITE, idx))

    clear_list: list[String] = []
    for info in clear:
        if info.data not in clear_list:
            clear_list.append(info.data)
            out.append(clear_region_code(info.data))
            out.append(debug_code(info.data, None))

    if have_null:
        out.append('.autoregion\n'
                   'null_txt:\n.db 0x00, 0x00\n'
                   '.endautoregion')
    for n in null:
        out.append(clear_region_code(n.data))
        out.append(debug_code(n.data, None))
        p_addr = []
        if n.ref:
            t = n.ref[0]
            base = t.addr
            p_addr = [GbaAddr(base.value + n.ref[1] * 4)]
        else:
            if n.data.p_addr:
                p_addr = n.data.p_addr
        for pa in p_addr:
            if pa.value < 0x8000000 or pa.is_not_word_align():
                print(f'ERROR: invalid ptr address "{pa}" of {n.data}')
            else:
                out.append(f'.org {pa}\n.dw org(null_txt)\n')

    overwrite: list[ImportInfo] = []
    reloc: list[ImportInfo] = []

    for index, info_list in idx_map.items():
        if not info_list:
            continue
        if len(info_list) == 1:
            info = info_list[0]
            if info.type is Type.RELOC:
                addr_map[index] = GbaAddr(0)
                reloc.append(info)
                out.append(clear_region_code(info.data))
                out.append(debug_code(info.data, index))
                if info.data.n_addr:
                    out.append(generate_area_code(
                        info.data, index, info.data.n_addr))
                    out.extend(generate_addr_code(info, info.data.n_addr))
                else:
                    out.append(generate_auto_region_code(info.data, index))
                    out.extend(generate_auto_addr_code(info))
            elif info.type is Type.OVERWRITE:
                addr_map[index] = info.data.addr
                info.new_addr = info.data.addr
                overwrite.append(info)
            continue

        count: dict[tuple[int, Type], int] = dict()

        move: list[ImportInfo] = []
        keep: list[ImportInfo] = []

        for info in info_list:
            addr = info.data.addr.value
            n_addr = info.data.n_addr
            if (n_addr and n_addr.value > 0x8000000 and
                    not n_addr.is_not_word_align()):
                move.append(info)
                out.append(clear_region_code(info.data))
                out.append(debug_code(info.data, index))
                out.append(generate_area_code(info.data, index, n_addr))
                out.extend(generate_addr_code(info, n_addr))
                continue
            if (addr, info.type) in count:
                count[(addr, info.type)] = count[(addr, info.type)] + 1
            else:
                count[(addr, info.type)] = 1
            keep.append(info)

        if move:
            n_addr = move[0].data.n_addr
            for info in keep:
                out.append(clear_region_code(info.data))
                out.append(debug_code(info.data, index))
                out.extend(generate_addr_code(info, n_addr))  # type: ignore
            continue
        if keep:
            n_addr, i_type = max_count(count)
            if i_type is Type.OVERWRITE:
                addr_map[index] = n_addr
                added = False
                remain: list[ImportInfo] = []
                for info in keep:
                    if n_addr == info.data.addr:
                        if not added:
                            info.new_addr = n_addr
                            overwrite.append(info)
                        else:
                            print(f'Skip {info.data}, ref={info.ref}, '
                                  f'{info.index} {info.type.name}')
                    else:
                        remain.append(info)
                for info in remain:
                    out.append(clear_region_code(info.data))
                    out.append(debug_code(info.data, index))
                    out.extend(generate_addr_code(info, n_addr))
            else:
                addr_map[index] = GbaAddr(0)
                info_0 = keep[0]
                out.append(generate_auto_region_code(info_0.data, index))
                for info in keep:
                    out.append(clear_region_code(info.data))
                    out.append(debug_code(info.data, index))
                    out.extend(generate_auto_addr_code(info))
    for info in overwrite:
        out.append(generate_overwrite_code(info))

    str_map_out = {k.decode('cp932'): v for k, v in str_map.items()}
    debug = {'str': str_map_out, 'idx': idx_map, 'addr': addr_map}
    with open(debug_path, 'w', encoding='utf-8') as f:
        json.dump(debug, f, ensure_ascii=False, indent=4, cls=InfoEncoder)

    tmp = [out[0]]
    for s in out[1:]:
        if s not in tmp:
            tmp.append(s)
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(tmp))
    with open(struc_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(struc))
    print(f'Write data to {text_path}, {struc_path}')


if __name__ == '__main__':
    main()
