# BadOS Dynamic Shell (bdsh)

import os
import sys

from bdsh.shell import Shell

def main():
    _cwd = os.getcwd()
    bdsh = Shell(sys.stdout, sys.stdin)
    bdsh.start()
    os.chdir(_cwd)

if __name__ == "__main__":
    main()