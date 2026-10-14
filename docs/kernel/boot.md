---
title: Boot Flow
parent: BadOS Kernel
nav_order: 3
---

# Boot flow

The ISO and direct-QEMU targets both start the Linux kernel with a compressed CPIO initramfs. The kernel command line selects:

```text
rdinit=/usr/bin/bdsh-init
```

`rdinit` selects the init program inside the initramfs. Buildroot installs the `bdsh-init` console entry point, which calls `bdsh.init:main`. That entry point creates the shell data directories and starts the minimal shell as user `default`; it does not ask for a login or start the BadLogon and network services.

## ISO menu

The GRUB menu in `kernel/iso/grub.cfg` provides two entries:

- **Start BadOS** uses the VGA virtual terminal (`tty0`).
- **Start BadOS (serial mode)** uses `ttyS0` at 115200 baud.

The shell accepts keyboard input through the selected console. In the graphical entry, focus the QEMU display window to type. The serial entry is intended for a connected serial console or a terminal attached to QEMU's serial output.

## Live filesystem and persistence

The CPIO filesystem is expanded into RAM at boot. Files created or changed during a session, including shell profiles and package installs, disappear when the machine shuts down. The ISO does not install BadOS to a disk or provide persistent user data.

## Entropy device

QEMU is configured with a virtio random-number device. The required kernel drivers expose it to the system; this supplies random data used by Python and password hashing during startup and login.
