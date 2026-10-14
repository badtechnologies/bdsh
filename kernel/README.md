# BadOS image build

The kernel build uses Buildroot 2025.02.18 in Docker Compose and exports boot images to `kernel/artifacts/`.

For prerequisites, current `make` targets, configuration, boot behavior, and image limitations, see the [BadOS kernel documentation](../docs/kernel/index.md).

The usual workflow from the repository root is:

```sh
docker volume create bados-build
make load-osconfig
make all
```

`make all` builds and checks the kernel and initramfs, exports them, and creates a BIOS/UEFI ISO. To boot the ISO with QEMU, use `make run`.
