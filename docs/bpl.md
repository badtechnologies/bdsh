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

## Creating packages

Packages should be contained in a folder with the name of the package.

In the package root, create a `bpl.json` file, with the following contents:

```json
{
 "name": "example bdsh package",
 "version": "1.0.0",
 "author": "Me!",
 "bin": "example.py",
 "homepage": "https://example.com",
 "requires": [
  "packagename",
  "another-package"
 ]
}
```

You can access a JSON schema for the `bpl.json` file at <https://raw.githubusercontent.com/badtechnologies/bdsh/main/bpl/bpl.schema.json>

Most of this is self-explanatory. The `bin` key should point to the script to download. `"main.py"` tells bpm to download `main.py` from your package root.
The file name will be discarded by bpm, and will be renamed to the name of your package. It is best practice to name your binary the same as your package.

Only `name`, `version`, and `author` must be included to make a valid package.

Not including `bin` will not download any binaries for your package; useful for package groups.

Not including `requires` will not download any dependencies.
