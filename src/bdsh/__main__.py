# BadOS Dynamic Shell (bdsh)

import os
from getpass import getpass

from bdsh import SHELL_COPYRIGHT
from bdsh.io.console import ConsoleTerminal
from bdsh.service import ServiceUnavailableError
from bdsh.service.badlogon import User
from bdsh.service.badlogon.client import BadLogonClient
from bdsh.service.dispatch import dispatch_system_services
from bdsh.session import Session
from bdsh.shell import Shell


def shell_login() -> User:
    client = BadLogonClient()

    print(SHELL_COPYRIGHT)

    user = None

    while not user:
        try:
            user = client.get_user_by_credentials(
                username=input("Username: "),
                password=getpass("Password: "))
            if not user:
                print("\nInvalid login")
        except ServiceUnavailableError:
            print("\nfatal: badlogon service unavailable, make sure the service is started and reachable")
            continue
        except KeyboardInterrupt:
            print()
            continue
    print()  # blank line between password field and shell prompt

    return User(**user)


def main():
    _cwd = os.getcwd()

    if os.getenv("BDSH_DISPATCH_SRV_PROC", "").lower() in ("true", "1"):
        print("proc: dispatching system services (BDSH_DISPATCH_SRV_PROC)")
        dispatch_system_services()

    user = shell_login()
    bdsh = Shell(Session(ConsoleTerminal(), user))
    bdsh.start()

    os.chdir(_cwd)


if __name__ == "__main__":
    main()
