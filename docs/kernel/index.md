---
title: BadOS Kernel
nav_order: 9
has_children: true
---

# BadOS kernel image

The `kernel/` tree builds a live x86_64 BadOS image. It uses Buildroot 2025.02.18 to build Linux and a compressed CPIO initramfs, then can wrap those images in a bootable BIOS/UEFI ISO.

The image starts `bdsh-init` as PID 1. It is a bootable shell environment, not a disk installer; the root filesystem is in RAM and is lost at shutdown.

## Guides

- [Building images](building.md): prerequisites, Make targets, and artifacts.
- [Configuration](configuration.md): Buildroot settings and required kernel options.
- [Boot flow](boot.md): initramfs startup, ISO boot entries, and persistence.

The source-level kernel build notes are in [`kernel/README.md`](https://github.com/badtechnologies/bdsh/blob/main/kernel/README.md).
