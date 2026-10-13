FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ARG BUILDROOT_VERSION=2025.02.18

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bc \
        bison \
        build-essential \
        ca-certificates \
        cpio \
        device-tree-compiler \
        file \
        flex \
        git \
        libelf-dev \
        libncurses-dev \
        libssl-dev \
        rsync \
        python3 \
        unzip \
        wget \
        xz-utils \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/buildroot \
    && wget -q "https://buildroot.org/downloads/buildroot-${BUILDROOT_VERSION}.tar.gz" \
        -O /tmp/buildroot.tar.gz \
    && tar -xzf /tmp/buildroot.tar.gz \
        --strip-components=1 -C /opt/buildroot \
    && rm /tmp/buildroot.tar.gz

COPY buildroot-entrypoint.sh /usr/local/bin/bados-buildroot
RUN chmod 0755 /usr/local/bin/bados-buildroot
