import argparse
import importlib
import pkgutil
from typing import List

import bdsh
from bdsh.command import Command
from bdsh.service import SERVICES, BadOSService


def _get_service(name: str) -> BadOSService:
    if name not in SERVICES:
        raise ValueError(f"unknown service: {name}")

    return SERVICES[name]()


def _discover_services():
    for module in pkgutil.walk_packages(bdsh.service.__path__, prefix=bdsh.service.__name__ + ".", ):
        importlib.import_module(module.name)


class BOSSCommand(Command):
    def __init__(self, session):
        super().__init__(session)
        _discover_services()

        self.parser = argparse.ArgumentParser(description="BadOS Service Supervisor (BOSS)", color=False)
        self.parser.add_argument('service', type=str, help='name of service to launch')

    def execute(self, args: List[str]):
        self.session.io.println("BadOS Service Supervisor, " + bdsh.SHELL_COPYRIGHT)

        args = self.parser.parse_args(args[1:])
        service = _get_service(args.service)
        try:
            self.session.io.println(f"Attempting to start {args.service}... SIGINT to stop")
            service.start()
        except ValueError as e:
            self.session.io.println(e)
            return
        except KeyboardInterrupt:
            service.stop()

    def help(self) -> str:
        pass
