---
title: Package Manager
nav_order: 5
---

# BadOS Package Manager (bpm)

`bpm` installs, removes, and upgrades packages from a GitHub-hosted BPL repository. The default repository is `badtechnologies/bpl/main`.

## Commands

```sh
bpm install <package> [package ...]
bpm remove <package> [package ...]
bpm upgrade <package> [package ...]
```

Add `-y` or `--yes` to skip confirmation prompts. To use a different repository, pass `-r owner/repository/branch`:

```sh
bpm install -y -r owner/repository/branch example
```

## Package layout

For package `example`, bpm fetches metadata from `lib/example/bpl.json`. The metadata's `id` is used for installed paths and must be a lowercase ID made of letters, digits, and hyphens.

- Binaries are downloaded from `lib/<id>/<filename>` and exposed under `bdsh/exec`.
- Package files are stored under `bdsh/app/<id>/<version>/`.
- Install records are stored under `bdsh/cfg/bpm/<id>@<version>.bpmstore`.
- `dependencies` names other packages to discover from the same repository.
- `pythonDependencies` names Python packages to install with pip.
- `setupScripts` names remote scripts that bpm executes during installation.

Only install packages and setup scripts from sources you trust. Setup scripts run as Python code in the installing environment.

## Upgrade and removal

`upgrade` removes the selected installed package and installs it again from the selected repository. `remove` deletes files and executable links recorded in its package store. Python dependencies installed for a package are not removed automatically.
