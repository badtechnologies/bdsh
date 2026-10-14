---
title: BOSS
nav_order: 6
---

# BOSS (BadOS Service Supervisor)

bdsh uses local services for login and networking. The built-in clients communicate with them over Unix-domain sockets.

## Service Management

The built-in `boss` command starts a registered service by name:

```sh
boss myservice.sys
```

The service runs in the foreground until interrupted. BOSS discovers the service classes shipped with bdsh and calls the selected service's `start()` method.

The `.sys` names are service identifiers, not files to execute. For the `boss` entry point and service lifecycle, see [Services](services.md).

## Installing Services

bdsh ships with the services listed in [Built-Ins](builtins.md).

Additional service packages can be installed with [bpm](../packages/index.md) and published through the [BPL](../packages/bpl.md).
