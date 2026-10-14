"""
Kernel entrypoint, run as PID 1 (/init).

Author: Logan Dhillon <dev@logandhillon.com>
"""

from bdsh.io.console import ConsoleTerminal
from bdsh.service.badlogon import User
from bdsh import OSPaths
from bdsh.session import Session
from bdsh.shell import Shell


def main():
    """This method is called as the kernel entrypoint, and starts the primary shell instance."""
    for path in (*OSPaths.all(), OSPaths.PROFILES.joinpath("default")):
        path.mkdir(parents=True, exist_ok=True)

    bdsh = Shell(Session(ConsoleTerminal(), User("default", "")))
    bdsh.start()


if __name__ == "__main__":
    main()
