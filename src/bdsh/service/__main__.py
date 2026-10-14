"""
Entrypoint for external service management via BOSS. Operates by
running a virtual shell to communicate with BOSS, to start the
service.

Author: Logan Dhillon <dev@logandhillon.com>
"""


import sys

from bdsh.io.console import ConsoleTerminal
from bdsh.service.badlogon import User
from bdsh.session import Session
from bdsh.shell import Shell

SERVICE_USER = User("boss", "")


def main():
    virtsh = Shell(Session(ConsoleTerminal(), SERVICE_USER))
    virtsh.execute("boss " + " ".join(sys.argv[1:]))


if __name__ == '__main__':
    main()
