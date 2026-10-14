SHELL := /bin/sh

COMPOSE ?= docker compose
QEMU ?= qemu-system-x86_64
JOBS ?= 4
MEMORY ?= 512M
ROOT_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
ARTIFACTS := $(ROOT_DIR)/kernel/artifacts
BDSH_SRC := $(ROOT_DIR)/src/bdsh

.PHONY: help load-osconfig update-osconfig menuconfig kernel-menuconfig \
	save-osconfig build reconfigure-kernel check export-build os-package \
	all run-direct run clean release

help:
	@printf '%s\n' \
		'BadOS build commands:' \
		'  make load-osconfig       	Initialize/reset Buildroot config from the tracked defconfig' \
		'  make menuconfig      		Configure Buildroot using the persistent Docker output volume' \
		'  make kernel-menuconfig 		Configure the kernel using the same Buildroot output' \
		'  make save-osconfig     		Save current Buildroot options to the tracked defconfig' \
		'  make reconfigure-kernel 		Re-apply tracked kernel config and fragments' \
		'  make build           		Build the kernel and root filesystem' \
		'  make check           		Check required kernel options and image contents' \
		'  make all             		Build a bootable BIOS/UEFI ISO in kernel/artifacts/' \
		'  make run-direct            	Build, export, and boot the image with macOS QEMU' \
		'  make run        				Boot ISO with graphics and serial attached to this terminal' \
		'' \
		'Override QEMU, JOBS, or MEMORY on the make command line as needed.'

load-osconfig:
	$(COMPOSE) run --rm --build buildroot init-config

update-osconfig:
	$(COMPOSE) run --rm --build buildroot olddefconfig

menuconfig:
	$(COMPOSE) run --rm --build buildroot menuconfig

kernel-menuconfig:
	$(COMPOSE) run --rm --build buildroot linux-menuconfig

save-osconfig:
	$(COMPOSE) run --rm --build buildroot savedefconfig

build:
	$(COMPOSE) run --rm --build buildroot build -j$(JOBS)
	$(COMPOSE) run --rm --build buildroot check
	mkdir -p "$(ARTIFACTS)"
	$(COMPOSE) run --rm --build buildroot export

all:
	$(MAKE) build
	$(COMPOSE) run --rm --build iso-builder

reconfigure-kernel:
	$(COMPOSE) run --rm --build buildroot linux-reconfigure


run-direct: 
ifeq ($(NO_BUILD),1)
	@echo "Skipping build, check, and export."
else
	$(MAKE) build
endif

	@command -v "$(QEMU)" >/dev/null 2>&1 || { \
		echo "QEMU not found: install it on macOS (for example: brew install qemu)" >&2; \
		exit 1; \
	}
	$(QEMU) \
		-m "$(MEMORY)" \
		-object rng-random,filename=/dev/urandom,id=rng0 \
		-device virtio-rng-pci,rng=rng0 \
		-kernel "$(ARTIFACTS)/bzImage" \
		-initrd "$(ARTIFACTS)/rootfs.cpio.gz" \
		-append "console=ttyS0,115200 rdinit=/usr/bin/bdsh-init" \
		-nographic

run:
ifeq ($(NO_BUILD),1)
	@echo "Skipping build, check, and ISO creation."
else
	$(MAKE) all
endif

	@command -v "$(QEMU)" >/dev/null 2>&1 || { \
		echo "QEMU not found: install it on macOS (for example: brew install qemu)" >&2; \
		exit 1; \
	}
	version=$$(sed -n 's/^__version__[[:space:]]*=[[:space:]]*"\([^"]*\)".*/\1/p' "$(BDSH_SRC)/__version__.py"); \
	test -n "$$version" || { echo "Could not read version" >&2; exit 1; }; \
	$(QEMU) \
		-m "$(MEMORY)" \
		-object rng-random,filename=/dev/urandom,id=rng0 \
		-device virtio-rng-pci,rng=rng0 \
		-serial stdio \
		-monitor none \
		-cdrom "$(ARTIFACTS)/BadOS-$$version-x86_64.iso" \
		-boot order=d

clean:
	$(COMPOSE) run --rm --build buildroot clean

release:
ifeq ($(NO_BUILD),1)
	@echo "Skipping build, check, and export."
else
	@printf 'This will delete all files in $(ARTIFACTS) and create a GitHub release. Continue? [y/N] '; \
	read answer; \
	case "$$answer" in \
		[yY]|[yY][eE][sS]) ;; \
		*) echo "Release cancelled."; exit 1 ;; \
	esac
	@set -eu; \
	rm -f "$(ARTIFACTS)"/*; \
	$(MAKE) all;
endif

	version=$$(sed -n 's/^__version__[[:space:]]*=[[:space:]]*"\([^"]*\)".*/\1/p' "$(BDSH_SRC)/__version__.py"); \
	test -n "$$version" || { echo "Could not read version" >&2; exit 1; }; \
	gh release create "v$$version" "$(ARTIFACTS)"/* --generate-notes