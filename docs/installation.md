---
title: Installation
nav_order: 2
---

# Installation

## Quick install

```sh
python3 -m pip install bdsh
python3 -m bdsh.install
```

The installer creates the shell root, config files, and the default user database.

## Manual setup

If you are working from source, run the install script directly:

```sh
python3 -m bdsh.install
```

The script does the following:

- installs the `requests` package if needed
- creates the `bdsh/` directory tree
- creates the initial user store
- installs the `core` package

## First run

Start bdsh with:

```sh
bdsh
```

The shell prompts for a username and password, then starts a new session in the user's profile directory.
