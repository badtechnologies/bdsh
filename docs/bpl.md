# BadOS Dynamic Shell Package Library (bpl)

Contains all packages avaliable to install for bdsh.

## What is `core`?

A file that contains all the system binaries that new installs of bdsh require.

## How to install packages?

Use the BPM (BadOS Package Manager) to install, remove, or otherwise manage packages.

Example: installing a package:

```sh
bpm install <package name>
```

For more information, run `bpm help`, or see the [bpm docs](bpm.md).

## Package URIs

Packages are located at

```url
https://raw.githubusercontent.com/badtechnologies/bdsh/main/bpl/<package name>
```
