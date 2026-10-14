---
title: File Structure
nav_order: 4
---

# Shell data files

bdsh stores its runtime data in a directory named `bdsh` under the process's current working directory. The path is chosen when Python imports bdsh; it is not a per-user home-directory setting.

| Path | Purpose |
| --- | --- |
| `bdsh/app/` | Versioned package files downloaded by bpm. |
| `bdsh/cfg/` | Configuration, the BadLogon user file, and bpm package records. |
| `bdsh/exec/` | Executables made available by package installs. bdsh searches this tree recursively. |
| `bdsh/prf/<username>/` | User profile directory; the normal shell starts the user here. |

The `OSPaths` class exposes these locations as `ROOT`, `APPLICATIONS`, `CONFIGS`, `EXECUTABLES`, and `PROFILES`.

## Files created by the system

- `bdsh/cfg/userman` stores usernames and Argon2 password hashes, one per line.
- `bdsh/cfg/bpm/*.bpmstore` records the package binaries and links used by bpm for removal.
- `bdsh/app/<package-id>/<version>/` contains downloaded package binaries.

On BadOS, the initramfs root filesystem is held in memory. Changes made to these paths during a live boot are lost when the system restarts.
