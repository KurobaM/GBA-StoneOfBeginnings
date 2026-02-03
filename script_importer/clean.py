# Copyright (C) 2026, KurobaM
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import re

if __name__ == '__main__':
    os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    folder = 'script'
    paths = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.split('.')[-1] == 'txt':
                paths.append(os.path.join(root, file))

    for fn in paths:
        with open(fn, 'r', encoding='utf-8') as f:
            data = f.read()
        cleaned = re.sub(r'(\r\n|\n)(\r\n|\n)+', '\n\n', data)
        cleaned = "\n".join(line.rstrip() for line in cleaned.splitlines())
        with open(fn, 'w', encoding='utf-8') as f:
            f.write(cleaned)
