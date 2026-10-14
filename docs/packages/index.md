---
title: Packages
nav_order: 7
---

# Packages

This section documents the BPL package format and selected packages.

## Package metadata

Each package lives under `lib/<package-name>/` in its GitHub repository and includes a `bpl.json` file. A minimal example is:

```json
{
  "name": "Example package",
  "id": "example",
  "version": "1.0.0",
  "author": "Example author",
  "shellVersion": ">=0.7.0",
  "binaries": {
    "example": "example.py"
  },
  "homepage": "https://example.com",
  "license": "MIT",
  "setupScripts": ["setup.py"],
  "dependencies": {
    "other-package": "*"
  },
  "pythonDependencies": {
    "some-library": ">=1.0.0"
  }
}
```

The required fields are `name`, `id`, `version`, `author`, and `shellVersion`. Versions use three numeric components. The `id` is the installed package name and should match the package's directory name. `binaries` maps command names to files in the package directory; setup scripts and Python dependencies are optional.

## Installing packages

Install a package with bpm:

```sh
bpm install <package>
bpm remove <package>
```

See [Package Manager](../bpm.md) for repository selection, install paths, and script behavior. Package-specific pages are notes about those packages, not a guarantee that the package is still published or current.
