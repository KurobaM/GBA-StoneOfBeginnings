# Copyright (C) 2025, KurobaM
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations
import hashlib
from io import BytesIO
import json
import math
import os
import sys
from tkinter import Tk, filedialog, messagebox


class Entry:
    def __init__(self, index: int, block_idx: int, block_count: int,
                 file_offset: int, file: bytes, new_block_idx: int | None = None,
                 new_block_count: int = 0, new_offset: int | None = None):
        self.block_idx = block_idx
        self.block_count = block_count
        self.file_offset = file_offset
        self.index = index
        self.new_block_idx = new_block_idx
        self.new_block_count = new_block_count
        self.new_file_offset = new_offset
        self.import_file = file

    def __repr__(self) -> str:
        return (
            f'<Entry {self.index}: {self.file_offset:x}'
            f', {self.block_count * 16} bytes => {self.new_file_offset:x}'
            f', {self.new_block_count * 16} bytes')


def parse_rom(start: int, end: int, orig_rom: bytes):
    if orig_rom[start + 2: start + 8] != b'\x01\x00\x04\x00\x00\x00':
        raise ValueError()
    count = int.from_bytes(orig_rom[start: start + 2], 'little')
    # sanity check
    le_offset = start + 8 + 8 * (count - 1)
    le_b_index = int.from_bytes(orig_rom[le_offset: le_offset+4], 'little')
    le_b_count = int.from_bytes(orig_rom[le_offset+4: le_offset+8], 'little')
    size = 16 * (le_b_index + le_b_count)
    if size != end - start:
        raise ValueError()
    data = orig_rom[start: start + size]
    entries: dict[int, Entry] = dict()
    for i in range(0, count):
        e_offset = 8 + 8 * i
        e_b_index = int.from_bytes(data[e_offset: e_offset+4], 'little')
        e_b_count = int.from_bytes(data[e_offset+4: e_offset+8], 'little')
        f_offset = start + e_b_index * 16
        f_data = data[e_b_index * 16: (e_b_index + e_b_count) * 16]
        entries[i] = Entry(i, e_b_index, e_b_count, f_offset, f_data)
    return entries


def get_import_file(dir_path: str):
    contents = os.listdir(dir_path)
    files: dict[int, bytes] = dict()
    for file_name in contents:
        file_path = os.path.join(dir_path, file_name)
        if os.path.isfile(file_path) and file_path.endswith('.psi3'):
            with open(file_path, 'rb') as f:
                files[int(file_name.split('.')[0], base=16)] = f.read()
    
    override_dir = os.path.join(os.path.dirname(__file__), 'override')
    override = os.listdir(override_dir)
    for file_name in override:
        file_path = os.path.join(override_dir, file_name)
        if os.path.isfile(file_path) and file_path.endswith('.psi3'):
            with open(file_path, 'rb') as f:
                print(f'Override: "{file_name}"')
                files[int(file_name.split('.')[0], base=16)] = f.read()
    return files


def build_data(start: int, end: int, orig_rom: bytes,
               entries: dict[int, Entry], files: dict[int, bytes], filemap: dict[str,str] | None = None):
    count = int.from_bytes(orig_rom[start: start + 2], 'little')
    data: list[bytes] = []
    data.append(orig_rom[start: start+8])
    print(f'Found {count} entries')
    last_idx = 0
    freed = 0
    non_empty = 0
    replace = 0
    for i in range(0, count):
        e = entries[i]
        if len(e.import_file) > 0:
            non_empty += 1
            if e.file_offset in files:
                freed += (math.ceil(len(e.import_file) / 16) * 16
                          - math.ceil(len(files[e.file_offset]) / 16) * 16)
                e.import_file = files[e.file_offset]
                replace += 1
        if e.block_count > 0:
            last_idx = i
    print(f'Found: {non_empty} files')
    print(f'Replace: {replace} files')
    print(f'Freed: {freed} bytes')
    if freed < 0:
        raise ValueError()
    first_data_block = math.ceil((8 + 8 * count) / 16)
    padding = b'0x00' * (first_data_block * 16 - 8 - 8 * count)
    for i in range(0, count):
        e = entries[i]
        if i == 0:
            e.new_block_idx = first_data_block
        else:
            prev = entries[i-1]
            if prev.new_block_idx is None:
                raise ValueError()
            e.new_block_idx = prev.new_block_idx + prev.new_block_count
        e.new_file_offset = start + 16 * e.new_block_idx
        e.new_block_count = math.ceil(len(entries[i].import_file) / 16)
        if last_idx == i:
            remain_size = end - start - 16 * e.new_block_idx
            e.new_block_count = remain_size // 16
        data.append(int.to_bytes(e.new_block_idx, 4, 'little'))
        data.append(int.to_bytes(e.new_block_count, 4, 'little'))
        if filemap is not None:
            filemap[f'{e.new_file_offset:x}'] = f'{e.file_offset:x}'
    data.append(padding)
    
    for i in range(0, count):
        e = entries[i]
        data.append(entries[i].import_file)
        data.append(b'\x00' * (16 * e.new_block_count - len(e.import_file)))
    out = b''.join(data)
    if len(out) != end - start:
        raise ValueError('Generated invalid data')
    return out


REGION_1 = {'start': 0x134AD9C, 'end': 0x135B91C}
REGION_2 = {'start': 0x1718FFC, 'end': 0x18C8D9C}


if __name__ == '__main__':
    info = False
    if len(sys.argv) < 5:
        root = Tk()
        root.withdraw()
        import_folder = filedialog.askdirectory(
            title='Select import file directory',
            initialdir='.', mustexist=True)
        orig_rom_path = filedialog.askopenfilename(
            title='Load Sword Craft Monogatari - Hajimari no Ishi ROM',
            initialdir='.', filetypes=[('GBA rom', '*.gba')])
        patched_rom_path = filedialog.askopenfilename(
            title='Load armips patched rom',
            initialdir='.', filetypes=[('armips patched rom', '*.gba')])
        export_path = filedialog.asksaveasfilename(
            title='Save to ...', initialdir='.',
            filetypes=[('GBA rom', '*.gba')])
        info = messagebox.askyesno(message='Write debug info?')
    else:
        import_folder = sys.argv[1]
        orig_rom_path = sys.argv[2]
        patched_rom_path = sys.argv[3]
        export_path = sys.argv[4]
    ok = True
    if not os.path.isdir(import_folder):
        ok = False
    if not os.path.isfile(orig_rom_path):
        ok = False
    if not os.path.isfile(patched_rom_path):
        ok = False
    if not ok:
        print('Invalid parameter')
        sys.exit(-1)
    print(f'Original file: {orig_rom_path}')
    print(f'armips output file: {patched_rom_path}')
    with open(orig_rom_path, 'rb') as f:
        orig_rom = f.read()
    with open(patched_rom_path, 'rb') as f:
        patched_rom = f.read()

    ref = '39bc4cf448106aa4b8cdde235632ffb57432c4b1919c8843510b70b3787fad2d'
    sha256 = hashlib.sha256(orig_rom).hexdigest()
    if (orig_rom[0xa0:0xaf] != b'CRAFTSWORD HB3C' or sha256 != ref):
        print('Invalid ROM')
        sys.exit(-1)

    files = get_import_file(import_folder)
    filemap = dict()
    print(f'Region: {REGION_1["start"]:x} - {REGION_1["end"]:x}')
    entries_1 = parse_rom(REGION_1['start'], REGION_1['end'], orig_rom)
    patch_1 = build_data(REGION_1['start'], REGION_1['end'],
                         orig_rom, entries_1, files, filemap)
    print(f'Region: {REGION_2["start"]:x} - {REGION_2["end"]:x}')
    entries_2 = parse_rom(REGION_2['start'], REGION_2['end'], orig_rom)
    patch_2 = build_data(REGION_2['start'], REGION_2['end'],
                         orig_rom, entries_2, files, filemap)
    mappath = os.path.join(os.path.dirname(__file__), 'psi3_map.json')
    with open(mappath, 'w') as f:
        json.dump(filemap, f)
    print(f'Save psi3 map to: {os.path.abspath(mappath)}')
    
    out = BytesIO(patched_rom)
    out.seek(REGION_1['start'])
    out.write(patch_1)
    out.seek(REGION_2['start'])
    out.write(patch_2)
    with open(export_path, 'wb') as f:
        f.write(out.getvalue())
    print(f'Export file path: {export_path}')

    if len(sys.argv) > 5:
        if '--write-info' in sys.argv[5:]:
            info = True
    if info:
        for e in entries_1.values():
            if len(e.import_file) > 0:
                print(repr(e))
        for e in entries_2.values():
            if len(e.import_file) > 0:
                print(repr(e))
