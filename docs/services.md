---
title: Services
nav_order: 6
---

# Services

bdsh uses lightweight Unix domain socket services for login and networking.

## badproc

The built in `badproc` command starts a service by name.

```sh
badproc network.badproc
badproc badlogon.badproc
```

The service manager discovers service classes at runtime and calls their `start()` method.

## Network service

The `network.badproc` service exposes these methods:

- `hostname`
- `resolve`
- `interfaces`
- `interface_addresses`

The shell commands `hostname`, `net`, and `ping` call these methods through the RPC client.

## BadLogon service

The `badlogon.badproc` service keeps the user database and validates login credentials.

It stores users in `bdsh/cfg/userman` and creates a profile directory under `bdsh/prf/<username>` when a user is loaded.

Each service listens on a socket in `/tmp` with the same name as its service registration.
