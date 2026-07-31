# BadOS Dynamic Shell (bdsh)

import os
import sys

from bdsh.service.badlogin import BadLoginService
from bdsh.shell import Shell


def main():
    _cwd = os.getcwd()

    user = BadLoginService().shell_login()
    bdsh = Shell(sys.stdout, sys.stdin, user)
    bdsh.start()

    os.chdir(_cwd)


if __name__ == "__main__":
    main()
