---
title: Installation
nav_order: 2
---

# Installation

## Install the Python package

Install bdsh from PyPI:

```sh
python3 -m pip install bdsh
```

The package requires Python 3.10 or newer and installs the `bdsh`, `bdsh-init`, and `boss` commands.

## Initialize a local shell root

Run the installer from the directory where you want the `bdsh/` data directory created:

```sh
python3 -m bdsh.install
```

The installer creates `bdsh/app`, `bdsh/cfg`, `bdsh/exec`, and `bdsh/prf`, then prompts you to create one or more users. If a `bdsh/` directory already exists, it asks before replacing its configuration. It also attempts to install the `core` package from the default package library.

The data directory is rooted at `./bdsh` relative to the process's current working directory; it is not automatically placed in your home directory.

## Start the shell

The normal `bdsh` command prompts for a username and password. It expects the BadLogon service to be running; start it separately with:

```sh
boss badlogon.sys
```

In a second terminal, run `bdsh`. See [Services](boss/services.md) for service lifecycle details.

For a minimal shell without login or services, run `bdsh-init`. It starts as the `default` user in the `bdsh/prf/default` profile directory, relative to the process's working directory. It is intended for the BadOS initramfs; see [Booting BadOS](kernel/boot.md).

## Install from source

From a checkout, install the project and test extras into the active Python environment:

```sh
python3 -m pip install -e ".[test]"
python3 -m pytest
```

See [Development](development.md) for the project layout and test workflow.
