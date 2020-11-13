# pacwatch

**pacwatch** is a utility which helps you watch important package updates in the [pacman](https://www.archlinux.org/pacman/) package manager.

![screenshot](screenshot.png)

## Usage

Simply run `python pacwatch.py`.

Or you can run `python pacwatch --reset` to reset to the default settings.

## Settings

The settings are stored in `~/.config/pacwatch/settings.yml`.

The structure is:

```yml
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
  - regex: (?:(\d+):)?(\d+)\.(\d+)\.(\d+)(.*)-(\d+) # each capture group of the regex is a part of the version
    parts: # the group of each part
      - epoch
      - major
      - minor
      - patch
      - identifier
      - pkgrel
  - regex: (?:(\d+):)?(\d+)\.(\d+)(.*)-(\d+)
    parts:
      - epoch
      - major-two
      - minor-two
      - identifier
      - pkgrel
  - regex: (?:(\d+):)?(\d+)-(\d+)
    parts:
      - epoch
      - single
      - pkgrel
verbose: # highlight some version changes at top, one package per line with the version change
  groups: # highlight all packages of certain groups
    - major
    - major-two
  extra: # extra verbose output for certain packages
    - packages: # the pacakges of a verbose rule
        - linux
        - linux-lts
      groups: # if the changes of the packages are in these groups, use verbose output
        - minor
        - patch
```
