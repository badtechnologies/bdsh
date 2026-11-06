"""The BOSS Service Executor starts the provided BadOSService class.
Created to be used in module runner.

```py
<this module> bdsh.service.myservice:MyService
```
"""

import importlib
import sys

from bdsh.service import BadOSService


def main():
    """Takes an fqn from argv, finds the BadOSService class corresponding, and starts it."""
    if len(sys.argv) != 2:
        print("invalid arguments provided! only pass the FQN of the service to run.")
        return

    module, qualname = sys.argv[1].split(":", 1)
    start_service(module, qualname)


def start_service(module: str, qualname: str):
    """Finds a BadOSService class and starts it

    Args:
        module (str): parent module of service class
        qualname (str): service class qualname
    """
    obj = importlib.import_module(module)

    for component in qualname.split("."):
        obj = getattr(obj, component)

    if not isinstance(obj, type) or not issubclass(obj, BadOSService):
        raise TypeError("expected argument to be a BadOSService")

    service = obj()
    service.start()


if __name__ == "__main__":
    main()
