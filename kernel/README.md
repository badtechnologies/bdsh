# BadOS Buildroot workflow

Buildroot is pinned to 2025.02.18 in `compose.yaml`. Docker Compose builds a
Linux build environment; named Docker volumes hold Buildroot's output and
download cache, keeping large build operations off macOS's shared workspace.
The `bdsh` Python project is mounted read-only into the container and installed
into the target root filesystem as a Buildroot Python package. Only the small
boot images are exported to `kernel/artifacts/`.

Install Docker Desktop and QEMU on macOS, then run these commands from the
repository root:

```sh
brew install qemu
make os-config
make os-build
make os-check
make os-export
make os-qemu
make os-iso
make os-qemu-iso
```

`make os-config` initializes or resets the output config from
`kernel/external/configs/bados_x86_64_defconfig`. Avoid running it after
menuconfig unless you intend to reset those selections. `make os-menuconfig`
and `make os-linux-menuconfig` use the same persistent output volume.

After editing Buildroot settings, persist them in the external tree with:

```sh
make os-save-config
```

Kernel options that must be built in are kept in
`kernel/external/board/bados/linux.config`. It is a fragment layered on
Buildroot's QEMU x86_64 kernel config, not a standalone Linux config. Keep the
QEMU baseline because it enables PCI and virtio prerequisites. Add changes to
the fragment after testing them in kernel menuconfig. `make os-build`
reconfigures Linux from the baseline and fragment before building, so generated
kernel config changes cannot silently be stale. Run `make os-linux-reconfigure`
to refresh just the kernel configuration without building the whole image.

`make os-qemu` builds, checks, exports, then runs QEMU interactively. Exit the
QEMU terminal with Ctrl-A then X. The CPIO image is an initramfs: its root
filesystem is recreated in RAM on every boot, so it is for boot testing, not
persistent storage.

`make os-iso` builds the same kernel and initramfs, then wraps them in a
hybrid BIOS/UEFI bootable ISO using GRUB. The versioned ISO is written to
`kernel/artifacts/BadOS-<version>-x86_64.iso`; `make os-qemu-iso` boots that ISO
in QEMU. The PC menu entry uses the display, while the serial entry is useful
for headless testing. You can write this ISO to optical media or a USB drive,
or attach it as virtual media. This is a live image: its root filesystem runs
from RAM and changes are lost on reboot. It does not install to a disk or
provide persistent user data.

The QEMU kernel command line explicitly selects
`rdinit=/usr/bin/bdsh-init` as PID 1. `rdinit` is required because the CPIO
initramfs contains its own `/init`; `init=` alone does not replace that
initramfs entry. Buildroot installs the selected console script from the
project's `bdsh-init = "bdsh.init:main"` entry point, so it invokes
`bdsh.init:main` directly. Linux mounts devtmpfs before starting init because
the kernel config enables `CONFIG_DEVTMPFS_MOUNT`. QEMU exposes its host
entropy source through a virtio RNG device; Python requires kernel random data
during startup. The Buildroot `bdsh` package also includes the Python
dependencies used by the shell, including ICMP support from the separate
`python-icmplib` package.

Useful optional settings:

```sh
make os-build JOBS=8
make os-qemu MEMORY=1G
make os-qemu QEMU=/path/to/qemu-system-x86_64
```

The Docker volumes are named `bados-build` and
`bados-buildroot-downloads`. They persist across container runs. Removing
those volumes discards the cached build and downloaded sources.
