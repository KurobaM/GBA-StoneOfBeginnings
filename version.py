from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import os
import re
import subprocess
import sys


@dataclass
class CommitInfo:
    hash: str
    author: str
    time: float
    cmt: str
    prev: CommitInfo | None = None
    next: CommitInfo | None = None


def eval_major(latest_major: CommitInfo | None) -> int:
    if latest_major is None:
        return 0
    match = re.match(r'Build v([0-9]+)\.0 \(.*?\)', latest_major.cmt)
    if not match:
        return 0
    major, = match.groups()
    return int(major)


def eval_build_type(author: str, latest_major: CommitInfo | None) -> str:
    if author != 'KurobaM':
        return 'private'
    if latest_major is None:
        return 'beta'
    match = re.match(r'Build v[0-9]+\.0 \((.*?)\)', latest_major.cmt)
    if not match:
        return 'beta'
    build_type, = match.groups()
    return build_type


def parse_build_str(value: str) -> tuple[int, int, int, str]:
    match = re.match(r'([0-9]+)\.([0-9]+)\.([0-9]+)_(.*?)$', value)
    if not match:
        major, minor, patch, build_type = ('0', '0', '0', 'beta')
    else:
        major, minor, patch, build_type = match.groups()
    return (int(major), int(minor), int(patch), build_type)


class BuildInfo:
    def __init__(self, commit_info: CommitInfo, major: int | None = None,
                 minor: int | None = None, patch: int | None = None,
                 build_type: str | None = None) -> None:
        self.commit = commit_info
        self.major = major
        self.minor = minor
        self.patch = patch
        self.type = build_type

    def __str__(self) -> str:
        return f'{self.major}.{self.minor}.{self.patch}_{self.type}'

    def get_version_info(self, date=False):
        if date:
            commit_time = datetime.fromtimestamp(self.commit.time)
            date_str = commit_time.strftime('%y%m%d')
            return f'{date_str}_{self.type}'
        else:
            return str(self)

    def __repr__(self) -> str:
        return (f'{self.commit.hash[:7]}, '
                f'{self.major}.{self.minor}.{self.patch}_{self.type}')

    def calc_minor_patch_value(
            self, release_history: dict[str, dict[str, str]]):
        change = eval_changes(self.commit.hash)
        prev = self.commit.prev
        if prev is None:
            return 0, 0
        if prev.hash in release_history:
            time_str = datetime.fromtimestamp(
                prev.time).strftime('%Y%m%d %H:%M:%S')
            if time_str in release_history[prev.hash]:
                _, minor, patch, _ = parse_build_str(
                    release_history[prev.hash][time_str])
                if change is ChangeType.MINOR:
                    return minor + 1, 0
                elif change is ChangeType.PATCH:
                    return minor, patch + 1
                else:
                    return minor, patch

        info = BuildInfo(prev)
        info.autofill_missing_info(release_history)
        if change is ChangeType.MINOR:
            return info.minor + 1 if info.minor is not None else 1, 0
        elif change is ChangeType.PATCH:
            return (info.minor if info.minor is not None else 0,
                    info.patch + 1 if info.patch is not None else 1)
        else:
            return info.minor, info.patch

    def autofill_missing_info(
            self, release_history: dict[str, dict[str, str]]):
        time_str = datetime.fromtimestamp(
            self.commit.time).strftime('%Y%m%d %H:%M:%S')
        if self.commit.hash in release_history:
            if time_str in release_history[self.commit.hash]:
                major, minor, patch, build_type = parse_build_str(
                    release_history[self.commit.hash][time_str])
                self.major = int(major)
                self.minor = int(minor)
                self.patch = int(patch)
                self.type = build_type
                return

        latest_major = get_latest_major_commit()
        if self.major is None:
            self.major = eval_major(latest_major)
        if self.type is None:
            build_type = eval_build_type(self.commit.author, latest_major)
            if self.commit.next is None:
                if is_dirty():
                    build_type = 'dirty'
            self.type = f'{build_type}-{self.commit.hash[:8]}'
        if self.minor is None or self.patch is None:
            self.minor, self.patch = self.calc_minor_patch_value(
                release_history)
        if 'dirty' in self.type:
            return
        release_history[self.commit.hash] = {
            time_str: f'{self.major}.{self.minor}.{self.patch}_{self.type}'}


def get_changes(commit_hash: str) -> list[str]:
    try:
        result = subprocess.run(
            ['git', 'show', commit_hash, '--name-only', '--pretty=format:'],
            check=True, capture_output=True, text=True, encoding='utf-8')
    except subprocess.CalledProcessError:
        return []
    else:
        return result.stdout.splitlines()


class ChangeType(Enum):
    NONE = 0
    MAJOR = 1
    MINOR = 2
    PATCH = 3


try:
    with open('version_config.json', 'r') as f:
        CHANGE_SOURCE = {k: ChangeType(v) for k, v in json.load(f).items()}
except Exception:
    CHANGE_SOURCE = {
        r'swordcraft3\.asm': ChangeType.MINOR,
        'asm/vwf_font.asm': ChangeType.PATCH,
        r'font/data/.*?\.bit': ChangeType.PATCH,
        r'font/data/.*?width\.bin': ChangeType.PATCH,
        'system_messages/': ChangeType.PATCH,
        'script/': ChangeType.PATCH,
        'gfx-scripts/': ChangeType.PATCH,
        r'asm/(?!vwf_font\.asm)': ChangeType.MINOR,
        'script_importer/override/': ChangeType.PATCH
    }
    with open('version_config.json', 'w') as f:
        json.dump({k: v.value for k, v in CHANGE_SOURCE.items()}, f)


def eval_changes(commit_hash: str):
    changes = get_changes(commit_hash)
    sources = CHANGE_SOURCE
    out = ChangeType.NONE
    for file in changes:
        change = ChangeType.NONE
        for pattern in sources.keys():
            if re.match(pattern, file):
                change = sources[pattern]
                break
        if change is not ChangeType.NONE:
            if change is ChangeType.MINOR:
                return change
            sources = {k: v for k, v in sources.items() if v != change}
            out = change
    return out


def get_current_commit():
    try:
        result = subprocess.run(
            ['git', 'log', '-1', r'--pretty=format:%H;%an;%at;%s'],
            check=True, capture_output=True, text=True, encoding='utf-8')
    except subprocess.CalledProcessError:
        return None
    else:
        output = result.stdout.splitlines()
        if not output:
            return None
        hash, author, timestamp, cmt = output[0].split(';', 3)
        out = CommitInfo(hash, author, float(timestamp), cmt)
        latest_major = get_latest_major_commit()
        older_hash = latest_major.hash if latest_major else ''
        commits = get_commits_between(older_hash, hash)
        current = out
        for commit in commits:
            current.prev = commit
            current.prev.next = current
            current = current.prev
        current.prev = latest_major
        if current.prev:
            current.prev.next = current
        return out


def get_commits_between(older_hash: str, newer_hash: str) -> list[CommitInfo]:
    commits: list[CommitInfo] = []
    if older_hash:
        cmd = f'{older_hash}..{newer_hash}~1'
    else:
        cmd = f'{newer_hash}~1'
    try:
        result = subprocess.run(
            ['git', 'log', cmd, r'--pretty=format:%H;%an;%at;%s'],
            check=True, capture_output=True, text=True, encoding='utf-8')
    except subprocess.CalledProcessError:
        return commits
    else:
        output = result.stdout.splitlines()
        for line in output:
            hash, author, timestamp, cmt = line.split(';', 3)
            commits.append(CommitInfo(hash, author, float(timestamp), cmt))
        return commits


def get_latest_major_commit():
    try:
        result = subprocess.run(
            [
                'git', 'log', '--grep', r"Build v[0-9]+\.0 \(.*?\)",
                '-E', r'--pretty=format:%H;%an;%at;%s'
            ],
            check=True, capture_output=True, text=True, encoding='utf-8')
    except subprocess.CalledProcessError:
        return None
    else:
        output = result.stdout.splitlines()
        if not output:
            return None
        hash, author, timestamp, cmt = output[0].split(';', 3)
        return CommitInfo(hash, author, float(timestamp), cmt)


def is_dirty():
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            check=True, capture_output=True, text=True, encoding='utf-8')
    except subprocess.CalledProcessError:
        return None
    else:
        return result.stdout != ''


if __name__ == '__main__':
    if '--date' in sys.argv:
        date = True
    else:
        date = False

    os.chdir(os.path.dirname(__file__))
    RELEASE_HISTORY: dict[str, dict[str, str]] = dict()

    config = 'release.json'
    try:
        with open(config, 'r') as f:
            RELEASE_HISTORY = json.load(f)
    except Exception:
        pass

    current_commit = get_current_commit()
    if current_commit is None:
        exit(0)

    rebuild_history = False
    if len(RELEASE_HISTORY) == 0:
        rebuild_history = True
    if not isinstance(next(iter(RELEASE_HISTORY.values())), dict):
        RELEASE_HISTORY = dict()
        rebuild_history = True
    if rebuild_history:
        current = current_commit
        while current.prev is not None:
            current = current.prev
        while current is not None:
            info = BuildInfo(current)
            info.autofill_missing_info(RELEASE_HISTORY)
            current = current.next
    info = BuildInfo(current_commit)
    info.autofill_missing_info(RELEASE_HISTORY)
    vinfo = info.get_version_info(date)

    with open(config, 'w') as f:
        json.dump(RELEASE_HISTORY, f)

    files = ['patches/swordcraft3.bps', 'patches/psi3_map.json']
    for file in files:
        name, ext = os.path.splitext(file)
        os.renames(file, f'{name}_v{vinfo}{ext}')
