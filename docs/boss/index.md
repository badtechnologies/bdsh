---
title: BOSS
nav_order: 6
---

# BOSS (BadOS Service Supervisor)

bdsh uses lightweight domain socket services for login and networking.

## Service Management

The built in `boss` command starts a service by name.

```sh
boss myservice.sys
```

BOSS discovers service classes at runtime and calls their `start()` method.

Services are conventionally stored as `.sys` files.

## Installing Services

BadOS ships with some services out-of-the-box (see [here](builtins.md)).

You can find and install more services using [bpm](../packages/index.md). Services can be published on
the [BDSH Package Library](../packages/bpl.md) just like other packages.