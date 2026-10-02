---
title: Packages
nav_order: 7
---

# Packages

This folder contains documentation for first- and third-party bdsh packages.

## Creating a package

Package repos are organized by package name.

Inside the package root, create a `bpl.json` file like this:

```json
{
  "name": "example bdsh package",
  "id": "example-bdsh-package",
  "version": "1.0.0",
  "author": "Me!",
  "binaries": {
    "example": "example.py"
  },
  "setupScripts": ["setup.py"],
  "homepage": "https://example.com",
  "license": "MIT",
  "shellVersion": "0.3.0",
  "dependencies": {
    "packagename": "*",
    "another-package": "^2.0.0"
  },
  "pythonDependencies": {
    "numpy": "*"
  }
}
```

The `binaries` field points to the files to download. The `setupScripts` list runs after installation. `shellVersion` is checked against the current bdsh version before installation.

Only `name`, `id`, `version`, `author`, and `shellVersion` are required to produce a valid package. The `id` should match the directory name in the package repo.

## Installing packages

Use the package manager to install or remove packages.

```sh
bpm install <package>
bpm remove <package>
```

For more information, see [Package Manager](../bpm.md).
