"""
A service is a type of process that does not need user interaction or
management, running in the background. Services are managed by BOSS.

Author: Logan Dhillon <dev@logandhillon.com>
"""


import signal
from abc import ABC, abstractmethod
from types import FrameType
from typing import Type

SERVICES: dict[str, Type["BadOSService"]] = {}


class BadOSService(ABC):
    """The base class for any service that can be ran or managed by BadOS."""
    name: str

    def __init__(self):
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

    def __init_subclass__(cls, name: str | None = None, **kwargs):
        super().__init_subclass__(**kwargs)

        if name is not None:
            cls.name = name
            if name in SERVICES:
                raise ValueError(f"service already registered: '{name}'")
            SERVICES[name] = cls

    @abstractmethod
    def start(self):
        ...

    @abstractmethod
    def stop(self):
        ...

    @abstractmethod
    def _handle_shutdown(self, signum: int, frame: FrameType | None):
        ...


class ServiceUnavailableError(OSError):
    def __init__(self, name: str):
        super().__init__(f"service unavailable: {name}")
