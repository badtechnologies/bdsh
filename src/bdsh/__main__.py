# BadOS Dynamic Shell (bdsh)

import os

from bdsh.io.console import ConsoleTerminal
from bdsh.service.badlogin import BadLoginService
from bdsh.session import Session
from bdsh.shell import Shell


def main():
    _cwd = os.getcwd()

    user = BadLoginService().shell_login()
    bdsh = Shell(Session(ConsoleTerminal(), user))
    bdsh.start()

    os.chdir(_cwd)


if __name__ == "__main__":
    main()
