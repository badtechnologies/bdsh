---
title: BadBandSSH
parent: Packages
nav_order: 2
---

# BadBandSSH (bssh)

BadBandSSH provides remote connections to a bdsh installation over SSH.

{: .headsup }
The note below reflects the behavior documented for BadBandSSH v0.9. Check the package's current BPL metadata and release notes before relying on it.

## Installation

```sh
bpm install bssh
```

## Usage

Run `bssh` to start a BadBandSSH server.

BadBandSSH runs on port 2200 by default. Connect to a BadBandSSH server with the following command:

```sh
ssh <username>@<hostname> -p 2200
```

The v0.9 note says remote sessions can run bdsh commands and definitions, but not installed binaries.
