---
title: Configuration
parent: BadOS Kernel
nav_order: 2
---

# Build configuration

The tracked Buildroot configuration is `kernel/external/configs/bados_x86_64_defconfig`. The Buildroot external tree lives under `kernel/external/`; Docker Compose keeps generated output and downloads in named Docker volumes instead of the macOS workspace.

## Buildroot options

The defconfig selects x86_64, Linux 6.12.27, Python 3, the local bdsh package, and a gzip-compressed CPIO root filesystem. It uses the QEMU x86_64 Linux configuration as a baseline, then adds `kernel/external/board/bados/linux.config` as a kernel fragment.

To change Buildroot selections interactively:

```sh
make menuconfig
make save-osconfig
```

To edit kernel options, use `make kernel-menuconfig` and save required settings in the tracked fragment. `make build` reapplies the baseline and fragment before compiling, so an edit made only to the generated kernel config will not be retained.

## Required kernel options

The image check verifies these are built into Linux:

- `CONFIG_DEVTMPFS` and `CONFIG_DEVTMPFS_MOUNT`, so device nodes are mounted before PID 1 starts.
- `CONFIG_HW_RANDOM`, `CONFIG_HW_RANDOM_VIRTIO`, `CONFIG_VIRTIO`, and `CONFIG_VIRTIO_PCI`, for QEMU's virtual random-number device.

The fragment also enables framebuffer console support. Keep Buildroot's QEMU kernel baseline: the fragment supplies BadOS requirements and is not a complete kernel configuration.

## Build checks

`make build` runs the image check after the build. It verifies the required kernel options, executable `/usr/bin/bdsh-init`, target Python interpreter, Python zlib extension, and generated `bzImage` and `rootfs.cpio.gz` images before exporting the boot artifacts.
