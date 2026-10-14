SHELL := /bin/sh

COMPOSE ?= docker compose
QEMU ?= qemu-system-x86_64
JOBS ?= 4
MEMORY ?= 512M
ROOT_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
ARTIFACTS := $(ROOT_DIR)/kernel/artifacts
BDSH_SRC := $(ROOT_DIR)/src/bdsh

.PHONY: help os-config os-update-config os-menuconfig os-linux-menuconfig \
	os-save-config os-build os-linux-reconfigure os-check os-export os-qemu \
	os-clean os-package release

help:
	@printf '%s\n' \
		'OS build commands:' \
		'  make os-config          Initialize/reset Buildroot config from the tracked defconfig' \
		'  make os-menuconfig      Configure Buildroot using the persistent Docker output volume' \
		'  make os-linux-menuconfig Configure the kernel using the same Buildroot output' \
		'  make os-save-config     Save current Buildroot options to the tracked defconfig' \
		'  make os-linux-reconfigure Re-apply tracked kernel config and fragments' \
		'  make os-build           Build the kernel and root filesystem' \
		'  make os-check           Check required kernel options and image contents' \
		'  make os-export          Copy bzImage and rootfs.cpio.gz into kernel/artifacts/' \
		'  make os-qemu            Build, export, and boot the image with macOS QEMU' \
		'' \
		'Override QEMU, JOBS, or MEMORY on the make command line as needed.'

os-config:
	$(COMPOSE) run --rm --build buildroot init-config

os-update-config:
	$(COMPOSE) run --rm --build buildroot olddefconfig

os-menuconfig:
	$(COMPOSE) run --rm --build buildroot menuconfig

os-linux-menuconfig:
	$(COMPOSE) run --rm --build buildroot linux-menuconfig

os-save-config:
	$(COMPOSE) run --rm --build buildroot savedefconfig

os-build:
	$(COMPOSE) run --rm --build buildroot build -j$(JOBS)

os-linux-reconfigure:
	$(COMPOSE) run --rm --build buildroot linux-reconfigure

os-check:
	$(COMPOSE) run --rm --build buildroot check

os-export:
	mkdir -p "$(ARTIFACTS)"
	$(COMPOSE) run --rm --build buildroot export

os-package:
	$(MAKE) os-build
	$(MAKE) os-check
	$(MAKE) os-export

os-qemu: 
ifeq ($(NO_BUILD),1)
	@echo "Skipping build, check, and export."
else
	$(MAKE) os-package
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

os-clean:
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
	$(MAKE) os-package; 
endif

	version=$$(sed -n 's/^__version__[[:space:]]*=[[:space:]]*"\([^"]*\)".*/\1/p' "$(BDSH_SRC)/__version__.py"); \
	test -n "$$version" || { echo "Could not read version" >&2; exit 1; }; \
	gh release create "v$$version" "$(ARTIFACTS)"/* --generate-notes