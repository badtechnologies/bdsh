---
title: Building Images
parent: BadOS Kernel
nav_order: 1
---

# Building BadOS

Run these commands from the repository root. Docker Compose builds Buildroot inside Linux containers, so install Docker Desktop (or Docker Engine with Compose) first. Install QEMU as well if you want to boot the output locally:

```sh
brew install qemu
docker volume create bados-build
```

`bados-build` is an external Docker volume used for Buildroot's persistent output. Compose creates the separate download-cache volume as needed. The build source is mounted read-only in the container; generated images are exported to `kernel/artifacts/`.

## Build

```sh
make load-osconfig
make build
```

`load-osconfig` resets the persistent Buildroot configuration from the tracked defconfig. Skip it when preserving existing menuconfig selections. If no config exists, `make build` initializes one automatically. The build target refreshes Linux and Python configuration, rebuilds the bdsh package, builds the system, checks required image contents, and exports the kernel and initramfs.

Build a bootable ISO after the image build:

```sh
make all
```

The ISO builder writes `kernel/artifacts/BadOS-<bdsh-version>-x86_64.iso`.

## Boot in QEMU

```sh
make run-direct
make run
```

`run-direct` boots the kernel and initramfs directly with a serial console. `run` boots the ISO with QEMU's graphical display and serial output attached to the launching terminal; use the ISO's serial menu entry for shell interaction through that terminal. QEMU uses 512 MB of memory by default.

## Make variables

Override defaults on the command line:

```sh
make build JOBS=8
make run MEMORY=1G
make run QEMU=/path/to/qemu-system-x86_64
```

`JOBS` defaults to `4`, `MEMORY` to `512M`, and `QEMU` to `qemu-system-x86_64`. Set `NO_BUILD=1` on either run target to boot previously built artifacts without rebuilding.

## Other targets

| Target                    | Purpose                                                                         |
| ------------------------- | ------------------------------------------------------------------------------- |
| `make update-osconfig`    | Reconcile the saved Buildroot configuration with the current defconfig options. |
| `make menuconfig`         | Open Buildroot's configuration menu.                                            |
| `make kernel-menuconfig`  | Open Linux kernel configuration.                                                |
| `make save-osconfig`      | Save the current Buildroot selections to the tracked defconfig.                 |
| `make reconfigure-kernel` | Reapply the tracked kernel baseline and fragment.                               |
| `make clean`              | Run Buildroot's clean target.                                                   |

`make release` deletes files under `kernel/artifacts/` after a confirmation prompt, rebuilds the ISO, then creates a GitHub release using `gh`. Use it only with the intended repository and GitHub CLI account authenticated.
