---
title: Built-Ins
parent: BOSS
nav_order: 2
---

# BOSS Built-Ins

BadOS ships with some services out-of-the-box, some are listed below.

## network.sys

This service exposes these methods:

- `hostname`
- `resolve`
- `interfaces`
- `interface_addresses`

The shell commands `hostname`, `net`, and `ping` call these methods through the RPC client.

## badlogon.sys

This service keeps the user database and validates login credentials.

It stores users in `bdsh/cfg/userman` and creates a profile directory under `bdsh/prf/<username>` when a user is loaded.
