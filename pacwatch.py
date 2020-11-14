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
__version__ = '0.3.2'
__settings_version__ = 2

settingsFile = Path(user_config_dir(appname=__prog__)) / 'settings.yml'

settings = {
    'settings_version': __settings_version__,
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
    'verbose': [
        {
            'packages': ['linux'],
            'regex': 'linux-(lts|zen|hardened)',
            'allGroups': True
        },
        {
            'packages': ['systemd'],
            'groups': ['minor-two'],
        },
        {
            'regex': 'lib.+',
            'allGroups': True,
            'no_verbose': True
        },
        {
            'regex': '.*',
            'groups': ['minor', 'minor-two'],
            'explicitOnly': True
        },
        {
            'regex': '.*',
            'groups': ['epoch', 'major', 'major-two']
        }
    ]
}


def saveSettings():
    os.makedirs(str(settingsFile.parent), exist_ok=True)
    with open(str(settingsFile), 'w') as f:
        yaml.safe_dump(settings, f, sort_keys=False)


def pacman(args: str, display: bool, noConfirm: bool = True):
    p = subprocess.run(f"{settings['pacman_command']} {'--noconfirm' if noConfirm else ''} {'--color=always' if display else ''} {args}",
                       capture_output=not display, check=noConfirm, shell=True)
    if not display:
        return p.stdout.decode().strip()


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


def showPackage(name, oldVersion, newVersion, verbose):
    if verbose:
        lcp = 0  # longest common prefix
        while lcp + 1 < len(oldVersion) and lcp + 1 < len(newVersion) and oldVersion[lcp] == newVersion[lcp]:
            lcp += 1
        print(
            f'{name}: {oldVersion[:lcp]}{colored(oldVersion[lcp:], "red")} -> {newVersion[:lcp]}{colored(newVersion[lcp:], "green")}')
    else:
        print(f'{name}-{newVersion}', end=' ')


explicitPackages = []


def isExplicit(name):
    global explicitPackages
    if len(explicitPackages) == 0:
        explicitPackages = pacman('-Qeq', False).split('\n')
    return name in explicitPackages


def matchVerboseRule(name, group, rule):
    if ('packages' in rule and name in rule['packages']) or ('regex' in rule and re.compile(rule['regex']).fullmatch(name)):
        if 'explicitOnly' in rule and rule['explicitOnly'] and not isExplicit(name):
            return False
        if 'allGroups' in rule and rule['allGroups']:
            return True
        if 'groups' in rule and group in rule['groups']:
            return True
    return False


def isVerbose(name, group):
    if 'verbose' not in settings:
        return False
    for rule in settings['verbose']:
        if matchVerboseRule(name, group, rule):
            if 'no_verbose' in rule and rule['no_verbose']:
                return False
            else:
                return True
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog=__prog__,
        description=f'{__prog__} is a pacman wrapper which helps you watch important package updates. Source code at https://github.com/ouuan/pacwatch.')
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

    if 'settings_version' not in settings or settings['settings_version'] != __settings_version__:
        print(f'''Incompatible changes of the settings detected.
Please manually update the settings or reset the settings to default.
You can use `{__prog__} --edit` or `{__prog__} --reset` to help you.''')
        quit()

    pacman('-Sy', True)

    oldVersion = {}
    for line in pacman('-Q', False).split('\n'):
        pkgName, pkgVer = line.split(' ')
        oldVersion[pkgName] = pkgVer

    newVersion = {}
    packagesOfGroup = {}
    for group in settings['groups']:
        packagesOfGroup[group] = []
    packagesOfGroup[None] = []

    for line in pacman('-Sup --print-format "%n %v"', False).split('\n'):
        pkgName, pkgVer = line.split(' ')
        if pkgName in oldVersion:
            oldVer = oldVersion[pkgName]
        else:
            oldName = pacman(f'-Qq {pkgName}', False)
            if oldName not in oldVersion:
                print(
                    f'{colored("WARN", "red")} Failed to find the update-available package {colored(pkgName, "cyan")} in the installed packages')
                continue
            oldVer = oldVersion[oldName]
        newVersion[pkgName] = pkgVer
        group = getGroup(oldVersion[pkgName], newVersion[pkgName])
        if isVerbose(pkgName, group):
            showPackage(pkgName, oldVersion[pkgName],
                        newVersion[pkgName], True)
        else:
            packagesOfGroup[group].append(pkgName)

    for group, packages in packagesOfGroup.items():
        packages.sort()
        if len(packages) > 0:
            if group == None:
                group = 'unknown'
            print(f'{colored(f"{group} ({len(packages)})", "magenta")}', end=' ')
            for package in packages:
                showPackage(
                    package, oldVersion[package], newVersion[package], False)
            print()

    pacman('-Su', True, False)
