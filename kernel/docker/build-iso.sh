#!/bin/sh
set -eu

ARTIFACTS=/workspace/kernel/artifacts
SOURCE=/workspace/bdsh
STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT

for image in bzImage rootfs.cpio.gz
do
	if [ ! -s "$ARTIFACTS/$image" ]; then
		echo "Required image not found: $ARTIFACTS/$image (run 'make os-package' first)" >&2
		exit 1
	fi
done

version=$(sed -n 's/^__version__[[:space:]]*=[[:space:]]*"\([^"]*\)".*/\1/p' \
	"$SOURCE/src/bdsh/__version__.py")
if [ -z "$version" ]; then
	echo "Could not read bdsh version for ISO filename." >&2
	exit 1
fi

mkdir -p "$STAGE/boot/grub"
cp "$ARTIFACTS/bzImage" "$STAGE/bzImage"
cp "$ARTIFACTS/rootfs.cpio.gz" "$STAGE/rootfs.cpio.gz"
cp "$SOURCE/kernel/iso/grub.cfg" "$STAGE/boot/grub/grub.cfg"

output="$ARTIFACTS/BadOS-${version}-x86_64.iso"
grub-mkrescue -o "$output" "$STAGE"
test -s "$output"
echo "Created $output (BIOS and UEFI boot)."
