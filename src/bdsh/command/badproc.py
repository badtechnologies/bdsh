import argparse
from typing import List

from bdsh import SHELL_COPYRIGHT
from bdsh.command import Command
from bdsh.service import SERVICES, Service


def _get_service(name: str) -> Service:
    if name not in SERVICES:
        raise ValueError(f"unknown service: {name}")

    return SERVICES[name]()


class BadProcessManagerCommand(Command):
    def __init__(self, session):
        super().__init__(session)

        self.parser = argparse.ArgumentParser(description="BadProc Service Manager", color=False)
        self.parser.add_argument('service', type=str, help='name of service to launch')

    def execute(self, args: List[str]):
        self.session.io.println("BadProc Service Manager, " + SHELL_COPYRIGHT)

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
