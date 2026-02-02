# Copyright (C) 2025, KurobaM
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations
import hashlib
import json
import os
import sys


if __name__ == '__main__':
    if len(sys.argv) < 2:
        delete = True
    else:
        delete = False if sys.argv[1] == '--keep' else True
    os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    folder = 'script'
    rom = 'build\\swordcraft3-test.gba'
    print('Checking script folder ...')
    scripts: dict[str, str] = dict()
    time: dict[str, float] = dict()
    paths: dict[str, str] = dict()
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.split('.')[-1] == 'txt':
                path = os.path.join(root, file)
                with open(path, 'rb') as f:
                    data = f.read()
                if file in scripts:
                    if scripts[file] == hashlib.sha256(data).hexdigest():
                        print('Found duplicated file in another location:'
                              f'"{paths[file]}"; skip "{path}"')
                        if delete:
                            print(f'Delete: {path}')
                            os.remove(path)
                    else:
                        if time[file] < os.path.getmtime(path):
                            print('Found different file with same name:'
                                  f' "{paths[file]}" ', end='')
                            print(f', older; using "{path}"')
                            if delete:
                                print(f'Delete: {paths[file]}')
                                os.remove(paths[file])
                            scripts[file] = hashlib.sha256(data).hexdigest()
                            time[file] = os.path.getmtime(path)
                            paths[file] = path
                        else:
                            print('Found different file with same name:'
                                  f' "{paths[file]}"; skip "{path}"')
                            if delete:
                                print(f'Delete: {path}')
                                os.remove(path)
                else:
                    scripts[file] = hashlib.sha256(data).hexdigest()
                    time[file] = os.path.getmtime(path)
                    paths[file] = path

    print('Checking scripts for change ...')
    config_path = os.path.join(os.path.dirname(__file__), 'tracking.json')

    if not os.path.exists(config_path):
        with open(config_path, 'w') as f:
            json.dump(scripts, f)
        changed = [fp for fp in scripts]
    else:
        with open(config_path, 'r') as f:
            old = json.load(f)
        changed: list[str] = []
        for script_name in scripts:
            if script_name not in old:
                changed.append(script_name)
                print(f'New script: {paths[script_name]}')
            else:
                if scripts[script_name] != old[script_name]:
                    changed.append(script_name)
                    print(f'Script "{script_name}" updated!')

    print('Create bat file for compiling changed scripts ...')
    commands: list[tuple[str, str]] = []
    for script_name in changed:
        path = paths[script_name]
        pos = script_name.split('.')[0]
        program_path = 'script_inserter\\swordcraft3c.exe'
        commands.append((script_name,
                         f'{program_path} {rom} {path} --pos={pos} --quiet\n'))
    bat = 'build/compile.bat'
    with open(bat, 'w') as f:
        f.write('echo --- Start compiling ----------------------\n')
        for name, command in commands:
            f.write(f'echo File {name}\n')
            f.write(command)
        f.write('echo --- Finished -----------------------------\n')
    print(f'Write script compile bat file: {bat}')
    print(f'Write {len(commands)} commands')
    with open(config_path, 'w') as f:
        json.dump(scripts, f)
