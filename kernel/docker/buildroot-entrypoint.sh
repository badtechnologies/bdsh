#!/bin/sh
set -eu

BR_SRC=/opt/buildroot
EXT=/workspace/kernel/external
OUT=/build/bados
DL_DIR=/downloads
DEFCONFIG="$EXT/configs/bados_x86_64_defconfig"

if [ ! -f "$BR_SRC/Makefile" ]; then
	echo "Buildroot source is missing from the build image: $BR_SRC" >&2
	exit 1
fi

if [ ! -f "$EXT/external.desc" ] || [ ! -f "$DEFCONFIG" ]; then
	echo "BadOS Buildroot external tree is incomplete under $EXT" >&2
	exit 1
fi

mkdir -p "$OUT" "$DL_DIR"

buildroot_make()
{
	make -C "$BR_SRC" \
		O="$OUT" \
		BR2_EXTERNAL="$EXT" \
		BR2_DL_DIR="$DL_DIR" \
		"$@"
}

initialize_config()
{
	buildroot_make defconfig BR2_DEFCONFIG="$DEFCONFIG"
}

command_name=${1:-all}
if [ "$#" -gt 0 ]; then
	shift
fi

case "$command_name" in
	init-config)
		initialize_config
		exit
		;;
	linux-reconfigure)
		buildroot_make linux-reconfigure "$@"
		exit
		;;
	build)
		if [ ! -f "$OUT/.config" ]; then
			echo "No persistent Buildroot config found; initializing from the tracked defconfig."
			initialize_config
		fi
		buildroot_make linux-reconfigure
		buildroot_make all "$@"
		exit
		;;
	savedefconfig)
		buildroot_make savedefconfig BR2_DEFCONFIG="$DEFCONFIG"
		exit
		;;
	check)
		;;
	export)
		;;
	*)
		if [ ! -f "$OUT/.config" ]; then
			echo "No persistent Buildroot config found; initializing from the tracked defconfig."
			initialize_config
		fi
		;;
esac

case "$command_name" in
	check)
		kernel_config=$(find "$OUT/build" -maxdepth 3 -type f \
			-path '*/linux-*/.config' -print -quit)
		if [ -z "$kernel_config" ]; then
			echo "Built Linux kernel config not found. Run 'make os-build' first." >&2
			exit 1
		fi

		missing_options=0
		for option in \
			CONFIG_DEVTMPFS \
			CONFIG_DEVTMPFS_MOUNT \
			CONFIG_HW_RANDOM \
			CONFIG_HW_RANDOM_VIRTIO \
			CONFIG_VIRTIO \
			CONFIG_VIRTIO_PCI
		do
			if ! grep -qx "${option}=y" "$kernel_config"; then
				echo "Required built-in kernel option missing: ${option}=y" >&2
				actual=$(grep -E "^(${option}=|# ${option} is not set)" "$kernel_config" || true)
				if [ -n "$actual" ]; then
					printf '  effective value: %s\n' "$actual" >&2
				else
					echo "  effective value: not present" >&2
				fi
				missing_options=1
			fi
		done
		if [ "$missing_options" -ne 0 ]; then
			echo "Kernel options are rebuilt from the tracked QEMU config and external fragment by 'make os-build'." >&2
			exit 1
		fi

		for path in \
			"$OUT/target/init" \
			"$OUT/target/sbin/bdsh-init" \
			"$OUT/target/usr/bin/python3" \
			"$OUT/images/bzImage" \
			"$OUT/images/rootfs.cpio.gz"
		do
			if [ ! -e "$path" ]; then
				echo "Required image file missing: $path" >&2
				exit 1
			fi
		done

		if [ ! -x "$OUT/target/init" ] || [ ! -x "$OUT/target/sbin/bdsh-init" ]; then
			echo "Init programs must be executable in the target filesystem." >&2
			exit 1
		fi

		echo "Image checks passed."
		echo "Kernel config: $kernel_config"
		;;
	export)
		for image in bzImage rootfs.cpio.gz
		do
			if [ ! -f "$OUT/images/$image" ]; then
				echo "Image not found: $OUT/images/$image (run 'make os-build' first)" >&2
				exit 1
			fi
		done
		mkdir -p /workspace/kernel/artifacts
		cp "$OUT/images/bzImage" /workspace/kernel/artifacts/bzImage
		cp "$OUT/images/rootfs.cpio.gz" /workspace/kernel/artifacts/rootfs.cpio.gz
		echo "Exported boot images to /workspace/kernel/artifacts."
		;;
	*)
		buildroot_make "$command_name" "$@"
		;;
esac
