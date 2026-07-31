import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bdsh.shell import Shell


def chdir(shell: Shell, path):
    shell.path = path
    os.chdir(path)