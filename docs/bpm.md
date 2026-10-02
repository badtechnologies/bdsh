---
title: Package Manager
nav_order: 5
---

# BadOS Package Manager (bpm)

Use `bpm` to install, remove, and upgrade packages.

The package manager is included in the shell. It resolves package metadata from the configured package repo and installs binaries and Python dependencies.

## Install a package

```sh
bpm install <package>
```

## Remove a package

```sh
bpm remove <package>
```

## Upgrade a package

```sh
bpm upgrade <package>
```

## Options

```sh
bpm install -y <package>
bpm install -r owner/repo/branch <package>
```

- `-y` skips the confirmation prompt.
- `-r` changes the package repo in the format `owner/repo/branch`.

## Package metadata

The package manager reads `bpl.json` from the package repo and installs each binary into `bdsh/app/<id>/<version>/`.

It also stores package metadata in `bdsh/cfg/bpm/*.bpmstore`.
