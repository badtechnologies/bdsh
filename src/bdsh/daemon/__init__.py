import importlib
import pkgutil
import signal
from abc import ABC, abstractmethod
from typing import Type

DAEMONS: dict[str, Type["Daemon"]] = {}


class Daemon(ABC):
    def __init__(self):
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

    def __init_subclass__(cls, name: str, **kwargs):
        super().__init_subclass__(**kwargs)
        if name in DAEMONS:
            raise ValueError(f"Daemon '{name}' is already registered!")
        DAEMONS[name] = cls

    @abstractmethod
    def start(self):
        ...

    @abstractmethod
    def stop(self):
        ...

    @abstractmethod
    def _handle_shutdown(self, signum, frame):
        ...


class DaemonUnavailableError(OSError):
    def __init__(self, daemon_name: str):
        super().__init__(f"daemon or socket unavailable: {daemon_name}")


def get_daemon(name: str) -> Daemon:
    # import all packages first to fight python lazy loading
    package = importlib.import_module(__name__)

    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
        importlib.import_module(f"{__name__}.{module_name}")

    # then find and execute specified daemon
    if name not in DAEMONS:
        raise ValueError(f"unknown daemon: {name}")

    cls = DAEMONS[name]
    daemon = cls()
    return daemon
