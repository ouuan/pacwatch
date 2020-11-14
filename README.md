# pacwatch

**pacwatch** is a [pacman](https://www.archlinux.org/pacman/) wrapper which helps you watch important package updates.

[![AUR version](https://img.shields.io/aur/version/pacwatch)](https://aur.archlinux.org/packages/pacwatch/)

![screenshot](screenshot.png)

## Installation

```sh
yay -S pacwatch
```

## Usage

Simply run `python pacwatch.py`, or `pacwatch` if you have installed it via AUR.

### Arguments

-   `-h, --help`: how this help message and exit
-   `--reset`: reset settings to default
-   `-e, --edit`: edit the settings in `$EDITOR`
-   `-v, --version`: show program's version number and exit

## Settings

The settings are stored in `~/.config/pacwatch/settings.yml`.

The structure is:

```yml
settings_version: 2 # the version of the setting, used to detect incompatible changes
pacman_command: sudo pacman # for example, you can use "yay" instead
groups: # groups of package version changes, the output will be in the same order
  - epoch
  - major
  - major-two
  - minor
  - minor-two
  - single
  - patch
  - identifier
  - pkgrel
rules: # rules to determine the group of a package change, choose the first matching rule
  - regex: (?:(\d+):)?(\d+)\.(\d+)\.(\d+)(.*)-([^-]+) # each capture group of the regex is a part of the version
    parts: # the group of each part
      - epoch
      - major
      - minor
      - patch
      - identifier
      - pkgrel
  - regex: (?:(\d+):)?(\d+)\.(\d+)(.*)-([^-]+)
    parts:
      - epoch
      - major-two
      - minor-two
      - identifier
      - pkgrel
  - regex: (?:(\d+):)?(\w+)(.*)-([^-]+)
    parts:
      - epoch
      - single
      - identifier
      - pkgrel
verbose: # the rules which determines which packages to be highlighted, checked one by one from top to bottom
  - packages: # these packages match this rule
      - linux
    regex: linux-(lts|zen|hardened) # the packages which fully matches this regex also match this rule
    allGroups: true # no matter what group the matching packages are in, they use verbose output
  - packages:
      - systemd
    groups: # only if a mathcing package is in these groups, it uses verbose output
      - minor-two
  - regex: lib.+
    allGroups: true
    no_verbose: true # the opposite of other rules: it prevents the packages it applies to using verbose output
  - regex: .* # matches all packages, which can be considered as a fallback or a default rule
    groups:
      - minor
      - minor-two
    explicitOnly: true # this rule only applies to explicitly installed packages, not dependencies
  - regex: .*
    groups:
      - epoch
      - major
      - major-two
```
