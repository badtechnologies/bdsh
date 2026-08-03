import sys

from bdsh.io.console import ConsoleTerminal
from bdsh.session import Session
from bdsh.shell import Shell
from bdsh.user import User

SERVICE_USER = User("BADPROC", "")


def main():
    virtsh = Shell(Session(ConsoleTerminal(), SERVICE_USER))
    virtsh.execute("badproc " + " ".join(sys.argv[1:]))


if __name__ == '__main__':
    main()
