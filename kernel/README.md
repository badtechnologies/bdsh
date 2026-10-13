# BadOS Buildroot workflow

Buildroot is pinned to 2025.02.18 in `compose.yaml`. Docker Compose builds a
Linux build environment; named Docker volumes hold Buildroot's output and
download cache, keeping large build operations off macOS's shared workspace.
Only the small boot images are exported to `kernel/artifacts/`.

Install Docker Desktop and QEMU on macOS, then run these commands from the
repository root:

```sh
brew install qemu
make os-config
make os-build
make os-check
make os-export
make os-qemu
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

Useful optional settings:

```sh
make os-build JOBS=8
make os-qemu MEMORY=1G
make os-qemu QEMU=/path/to/qemu-system-x86_64
```

The Docker volumes are named `bados-build` and
`bados-buildroot-downloads`. They persist across container runs. Removing
those volumes discards the cached build and downloaded sources.
