---
title: Built-Ins
parent: BOSS
nav_order: 2
---

# BOSS Built-In Services

bdsh registers two built-in services:

## network.sys

This service exposes these methods:

- `hostname`
- `resolve`
- `interfaces`
- `interface_addresses`

The `hostname`, `net`, and `ping` commands use this service through the RPC client. `ping` uses `resolve` here and sends ICMP requests with `icmplib`.

## badlogon.sys

This service validates login credentials and keeps the user database.

It stores usernames and Argon2 password hashes in `bdsh/cfg/userman`. Loading the database creates profile directories under `bdsh/prf/<username>`. The `bdsh` login flow requires this service to be running; `bdsh-init` does not use it.

See [Services](services.md) for how to start the services and how their RPC sockets work.
