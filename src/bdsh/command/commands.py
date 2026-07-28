from typing import List

from bdsh.command import ICommand
from bdsh.shell import Shell, NL


class HelpCommand(ICommand):
    def execute(self, args: List[str], shell: Shell):
        shell.print(f"bdsh commands:{NL}" + '\t'.join(shell.commands.keys()))

    def help(self) -> str:
        pass