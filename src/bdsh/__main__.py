# BadOS Dynamic Shell (bdsh)

import os
import sys

from bdsh.shell import Shell

if __name__ == "__main__":
    _cwd = os.getcwd()
    bdsh = Shell(sys.stdout, sys.stdin)
    bdsh.start()
    os.chdir(_cwd)
