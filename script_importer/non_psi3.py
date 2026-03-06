# Copyright (C) 2026, KurobaM
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations
import os
import sys

from common import load_json, save_json, GbaAddr, SjisString, FORMAT_VERSION

    
sjis = [SjisString([GbaAddr(0x80A4560)], GbaAddr(0x80C0178),0x14,
                'εの効果が切れた\x00\x00\x00\x00'),
     SjisString([GbaAddr(0x806E778)], GbaAddr(0x80BB778),0x10,
                '＜預かり武器＞\x00\x00'),
     SjisString([GbaAddr(0x806E7A4), GbaAddr(0x806E7CC),
                 GbaAddr(0x806E7F0)], GbaAddr(0x80BB788), 0x14,
                '−−−空き−−−\x00\x00\x00\x00'),
     SjisString([GbaAddr(0x806E7F8)], GbaAddr(0x80BB79C),0x14,
                '終了　　　　　　\x00\x00\x00\x00')]


if __name__ == '__main__':
    out = {hex(s.addr.value) : s for s in sjis}
    out['__version__'] = FORMAT_VERSION
    path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', 'script/non_psi3', 'data.json'))
    if os.path.isfile(path):
        data = load_json(path)
        if data['__version__'] != FORMAT_VERSION:
            print('Data format changed. Manual intervention required.')
            sys.exit(1)
        for key in out:
            if key not in data:
                data[key] = out[key]
        save_json(data, path)
    else:
        save_json(out, path)
    print(f'Save data to {path}') 
        
