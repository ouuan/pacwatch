#!/usr/bin/env python3

"""
   Copyright 2020 Yufan You

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import os
import re
import yaml
import argparse
import subprocess
from pathlib import Path
from termcolor import colored
from appdirs import user_config_dir

__prog__ = 'pacwatch'
__version__ = '0.2.2'

settingsFile = Path(user_config_dir(appname=__prog__)) / 'settings.yml'

settings = {
    'pacman_command': 'sudo pacman',
    'groups': [
        'epoch',
        'major',
        'major-two',
        'minor',
        'minor-two',
        'single',
        'patch',
        'identifier',
        'pkgrel'
    ],
    'rules': [
        {
            'regex': r'(?:(\d+):)?(\d+)\.(\d+)\.(\d+)(.*)-(\d+)',
            'parts': ['epoch', 'major', 'minor', 'patch', 'identifier', 'pkgrel']
        },
        {
            'regex': r'(?:(\d+):)?(\d+)\.(\d+)(.*)-(\d+)',
            'parts': ['epoch', 'major-two', 'minor-two', 'identifier', 'pkgrel']
        },
        {
            'regex': r'(?:(\d+):)?(\d+)-(\d+)',
            'parts': ['epoch', 'single', 'pkgrel']
        }
    ],
    'verbose': {
        'groups': ['major', 'major-two'],
        'extra': [
            {
                'packages': ['linux', 'linux-lts'],
                'groups': ['minor', 'patch']
            }
        ]
    }
}


def saveSettings():
    os.makedirs(str(settingsFile.parent), exist_ok=True)
    with open(str(settingsFile), 'w') as f:
        yaml.safe_dump(settings, f, sort_keys=False)


def pacman(args: str, display: bool, noConfirm: bool = True):
    p = subprocess.run(f"{settings['pacman_command']} {'--noconfirm' if noConfirm else ''} {'--color=always' if display else ''} {args}",
                       capture_output=not display, check=noConfirm, shell=True)
    if not display:
        return p.stdout.decode()


def getGroup(old: str, new: str):
    for rule in settings['rules']:
        regex = re.compile(rule['regex'])
        oldMatch = regex.fullmatch(old)
        newMatch = regex.fullmatch(new)
        if oldMatch and newMatch:
            for index, group in enumerate(rule['parts']):
                if index >= regex.groups:
                    break
                if oldMatch.group(index + 1) != newMatch.group(index + 1):
                    return group


def showPackage(name, oldVersion, newVersion, verbose, showed):
    if name in showed:
        return
    showed[name] = True
    if verbose:
        lcp = 0  # longest common prefix
        while lcp + 1 < len(oldVersion) and lcp + 1 < len(newVersion) and oldVersion[lcp] == newVersion[lcp]:
            lcp += 1
        print(
            f'{name}: {oldVersion[:lcp]}{colored(oldVersion[lcp:], "red")} -> {newVersion[:lcp]}{colored(newVersion[lcp:], "green")}')
    else:
        print(f'{name}-{newVersion}', end=' ')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog=__prog__,
        description=f'{__prog__} is a utility which helps you watch important package updates in the pacman package manager. Source code at https://github.com/ouuan/pacwatch.')
    parser.add_argument('--reset', action='store_true',
                        help='reset settings to default')
    parser.add_argument('-e', '--edit', action='store_true',
                        help='edit the settings in $EDITOR')
    parser.add_argument('-v', '--version', action='version',
                        version=f'%(prog)s {__version__}')
    parserResult = parser.parse_args()

    if parserResult.reset:
        saveSettings()
    else:
        try:
            with settingsFile.open() as f:
                settings = yaml.safe_load(f)
        except FileNotFoundError:
            saveSettings()

    if parserResult.edit:
        subprocess.run(f'{os.getenv("EDITOR")} {settingsFile}', shell=True)

    if parserResult.reset or parserResult.edit:
        quit()

    pacman('-Sy', True)

    oldVersion = {}
    for line in pacman('-Q', False).split('\n'):
        if len(line) <= 1:
            continue
        pkgName, pkgVer = line.split(' ')
        oldVersion[pkgName] = pkgVer

    newVersion = {}
    groupOfPkg = {}
    for line in pacman('-Sup --print-format "%n %v"', False).split('\n'):
        if len(line) <= 1:
            continue
        pkgName, pkgVer = line.split(' ')
        newVersion[pkgName] = pkgVer
        groupOfPkg[pkgName] = getGroup(oldVersion[pkgName], pkgVer)

    showed = {}

    for rule in settings['verbose']['extra']:
        for package in rule['packages']:
            if package not in groupOfPkg:
                continue
            if groupOfPkg[package] in rule['groups']:
                showPackage(
                    package, oldVersion[package], newVersion[package], True, showed)

    packagesOfGroup = {}
    for group in settings['groups']:
        packagesOfGroup[group] = []
    packagesOfGroup[None] = []

    for package, group in groupOfPkg.items():
        if not package in showed:
            packagesOfGroup[group].append(package)

    for packages in packagesOfGroup.values():
        packages.sort()

    for group in settings['verbose']['groups']:
        for package in packagesOfGroup[group]:
            showPackage(
                package, oldVersion[package], newVersion[package], True, showed)
        packagesOfGroup.pop(group)

    for group, packages in packagesOfGroup.items():
        if len(packages) > 0:
            if not group:
                group = 'unknown'
            print(f'{colored(f"{group} ({len(packages)})", "magenta")}', end=' ')
            for package in packages:
                showPackage(
                    package, oldVersion[package], newVersion[package], False, showed)
            print()

    pacman('-Su', True, False)
