# BadOS Dynamic Shell (bdsh)

import os

from bdsh.io.console import ConsoleTerminal
from bdsh.service.badlogin import BadLoginService
from bdsh.service.dispatch import dispatch_system_services
from bdsh.session import Session
from bdsh.shell import Shell


def main():
    _cwd = os.getcwd()

    if os.getenv("BDSH_DISPATCH_SRV_PROC", "").lower() in ("true", "1"):
        print("proc: dispatching system services (BDSH_DISPATCH_SRV_PROC)")
        dispatch_system_services()

    user = BadLoginService().shell_login()
    bdsh = Shell(Session(ConsoleTerminal(), user))
    bdsh.start()

    os.chdir(_cwd)


if __name__ == "__main__":
    main()
