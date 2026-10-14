---
title: Services
parent: BOSS
nav_order: 1
---

# Services

Services are registered Python classes that run in the background or provide an API to the shell. The built-in services are `badlogon.sys` and `network.sys`; see [Built-Ins](builtins.md).

## Starting a built-in service

Run `badproc` in a terminal for each service:

```sh
badproc badlogon.sys
badproc network.sys
```

Each process remains in the foreground. Stop it with Ctrl-C. The `boss <service>` shell command starts the same service from an interactive shell. The normal `bdsh` login needs `badlogon.sys`; network-related commands need `network.sys`.

For a shell session that manages its services itself, set `BDSH_DISPATCH_SRV_PROC=true` (or `1`) before running `bdsh`. This dispatches both built-in services on background threads before the login prompt.

## Service registration and RPC

BOSS discovers the service classes under `bdsh.service`. A service registers its identifier with `BadOSService` and implements `start()`, `stop()`, and shutdown handling. RPC methods must be marked with `@servicemethod`; the dispatcher only exposes marked methods.

The built-in RPC services use Unix-domain stream sockets under `/tmp`, named `/tmp/<service-name>.sock`. Clients exchange JSON requests containing an ID, method, and named parameters. Responses contain either a result or a remote error. Unsupported non-JSON values are rejected.

RPC is local to the host. Do not expose these sockets as a remote or authenticated network API.
