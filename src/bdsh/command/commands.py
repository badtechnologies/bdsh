import os
from typing import List, TYPE_CHECKING

from bdsh import NL
from bdsh.command import ICommand, Command

if TYPE_CHECKING:
    from bdsh.shell import Shell


class HelpCommand(ICommand):
    def execute(self, args: List[str]):
        self.shell.print(f"bdsh commands:{NL}" + '\t'.join(self.shell.commands.keys()))

    def help(self) -> str:
        pass


class ListDirectoryCommand(ICommand):
    def execute(self, args: List[str]):
        try:
            path = self.shell.get_path(args[1]) if len(args) > 1 else self.shell.path
            items = os.listdir(path)
            self.shell.print('\t'.join([item + '/' if os.path.isdir(os.path.join(path, item)) else item for item in items]))
        except FileNotFoundError:
            raise FileNotFoundError(f"{args[1]}: does not exist")

    def help(self) -> str:
        pass


class DefineCommand(ICommand):
    def execute(self, args: List[str]):
        if '-h' in args or '--help' in args:
            self.shell.print(
                f"usage: def <keyword> <definition>{NL}binds <keyword> to <definition>{NL}executing <keyword> will execute <definition>")
            return

        if len(args) < 3:
            raise ValueError("missing params (at least 3)")

        definition = " ".join(args[2:])

        if args[1] == definition:
            raise SyntaxError("keyword cannot be the same as the definition")

        self.shell.definitions[args[1]] = definition
        self.shell.print(f"defined '{args[1]}' to run '{definition}'")

    def help(self) -> str:
        pass


class ThrowCommand(ICommand):
    def execute(self, args: List[str]):
        raise Exception(' '.join(args[1:]))

    def help(self) -> str:
        pass


class GoCommand(ICommand):
    def execute(self, args: List[str]):
        if os.path.exists(path := self.shell.get_path(args[1])):
            self.shell.path = path
            os.chdir(path)
        else:
            raise FileNotFoundError(f"{args[1]}: no such file or folder")

    def help(self) -> str:
        pass


class PeekCommand(ICommand):
    def execute(self, args: List[str]):
        if os.path.isfile(path := os.path.join(self.shell.path, args[1])):
            with open(path, 'r') as f:
                self.shell.print(f.read())
        else:
            raise FileNotFoundError(f"{args[1]}: no such file")

    def help(self) -> str:
        pass


def register_commands(shell: Shell):
    return {
        "exit": Command(shell, lambda _: exit(0), ""),
        "help": HelpCommand(shell),
        "echo": Command(shell, lambda args: shell.print(' '.join(args[1:])), ""),
        "ld": ListDirectoryCommand(shell),
        "ver": Command(shell, lambda _: shell.print(shell.header), ""),
        "def": DefineCommand(shell),
        "throw": ThrowCommand(shell),
        "cwd": Command(shell, lambda _: shell.print(shell.cwd()), ""),
        "go": GoCommand(shell),
        "peek": PeekCommand(shell),
    }
