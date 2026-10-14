---
title: Home
nav_order: 1
---

# BadOS Dynamic Shell (bdsh)

bdsh is a Python shell for BadOS. It provides built-in commands, user profiles, package installs, and small system services.

## Get started

Install bdsh and create its working directory and user database with the [installation guide](installation.md). Then start the shell with:

```sh
bdsh
```

The interactive shell needs the BadLogon service running. See [Services](boss/services.md) for how to start it.

## BadOS kernel image

This repository also builds a live x86_64 BadOS image using Buildroot and Linux. The [kernel guide](kernel/index.md) explains how to build, configure, and boot it.
