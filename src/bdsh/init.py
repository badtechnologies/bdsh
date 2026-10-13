# BadOS Dynamic Shell (bdsh)

from bdsh.io.console import ConsoleTerminal
from bdsh.service.badlogon import User
from bdsh import OSPaths
from bdsh.session import Session
from bdsh.shell import Shell


def main():
    for path in (*OSPaths.all(), OSPaths.PROFILES.joinpath("default")):
        path.mkdir(parents=True, exist_ok=True)

    bdsh = Shell(Session(ConsoleTerminal(), User("default", "")))
    bdsh.start()


if __name__ == "__main__":
    main()
