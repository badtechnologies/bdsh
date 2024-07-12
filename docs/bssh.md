[❮ Back](.)

# BadBandSSH (bssh)

BadBandSSH allows remove connections into your bdsh installation via the SSH protocol.

> #### ⚠️ Heads up!
> BadBandSSH v0.9 does not support the use of binaries yet. Only bdsh commands and definitions can be run through BadBandSSH.

## Installation

```sh
bpm install bssh
```

## Usage

Run the `bssh` command to start a BadBandSSH server.

BadBandSSH runs on port 2200 by default. Connect to a BadBandSSH server with the following command:

```sh
ssh <username>@<hostname> -p 2200
```
