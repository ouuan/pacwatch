## UNRELEASED

## 1.2.2

Depend on the maintained fork `platformdirs` instead of the deprecated `appdirs`.

## 1.2.1

Add error handling for displaying pacman errors.

## 1.2.0

Group highlighted packages that share the same old and new versions.

## 1.1.2

Use `/usr/bin/python3` instead of `/usr/bin/env python3` to run it. This prevents using pyenv where the dependencies might be missing.

## 1.1.1

Show pacman output on error like broken dependencies.

## 1.1.0

Add `-p,--pacman_command` options so that you can toggle between `sudo pacman` and an AUR helper without modifying the settings.

## 1.0.1

Catch KeyboardInterrupt and don't show the error message.

## 1.0.0

Make not installed packages configurable.

## 0.4.2

Update the default settings to identify more version tags.

## 0.4.1

Fix the error when there's no available update.

## 0.4.0

-   Support `no_verbose` and `regex` in the verbose rules. (#4 and #5)
-   Support `explicitOnly` in the verbose rules. (#6)
-   Restructure the verbose rules.
-   Handle new packages.

## 0.3.2

Change `$pkgver-pacwatch.py` to `pacwatch-$pkgver.py`.

## 0.3.1

Specify pkgver in the source file name in PKGBUILD to make it unique.

## 0.3.0

Add the `always` attribute in verbose settings.

## 0.2.4

The description of pacwatch is slightly modified.

## 0.2.3

Fixed the default settings where "epoch" was not in the verbose groups.

## 0.2.2

Fixed the version number.

## 0.2.1

Release on AUR.

## 0.2.0

Use `--edit` to edit the settings.
