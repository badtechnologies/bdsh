---
title: Packages
nav_order: 6
---

# Packages

This folder contains documentation for first- and third-party packages.

## Creating packages

Packages should be contained in a folder with the name of the package.

In the package root, create a `bpl.json` file, with the following contents:

```json
{
  "name": "example bdsh package",
  // unique id for identifing this package, must be the same as the folder name
  "id": "example-bdsh-package",
  "version": "1.0.0",
  "author": "Me!",
  // files here will be added to the users 'exec' folder
  "binaries": {
    "example": "example.py"
  },
  // files here will run on install
  "setupScripts": [
    "setup.py"
  ],
  "homepage": "https://example.com",
  "license": "MIT",
  "shellVersion": "^0.3.0",
  "dependencies": {
    "packagename": "*",
    "another-package": "^2.0.0"
  },
  "pythonDependencies": {
    "numpy": "*"
  }
}
```

You can access a JSON schema for the `bpl.json` file
at <https://raw.githubusercontent.com/badtechnologies/bpl/main/bpl.schema.json>

Most of this is self-explanatory. The `binaries` key should point to the script(s) to download. `"example.py"` tells bpm
to download `example.py` from your package root.

Only `name`, `id` `version`, `author`, and `shellVersion` must be included to make a valid package. The `id` must match
the folder name on the package repo (i.e. BPL).

Not including `binaries` will not download any binaries for your package; useful for package groups.

Not including `dependencies` or `pythonDependencies` will not download any dependencies.

## Installing Packages

Use the BPM (BadOS Package Manager) to install, remove, or otherwise manage packages.

Example: installing a package:

```sh
bpm install <package name>
```

For more information, run `bpm help`, or see the [bpm docs](../bpm.md).