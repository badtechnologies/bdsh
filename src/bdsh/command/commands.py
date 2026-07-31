import os
from typing import List, TYPE_CHECKING, Dict

from bdsh import NL
from bdsh.command import Command, AnonymousCommand
from bdsh.command.bpm import BadOSPackageManagerCommand
from bdsh.command.net import NetCommand, HostnameCommand, PingCommand

if TYPE_CHECKING:
    from bdsh.shell import Shell


class HelpCommand(Command):
    def execute(self, args: List[str]):
        if len(args) > 1:
            subcommand = self.shell.commands.get(args[1])
            if isinstance(subcommand, Command):
                msg = subcommand.help()

                if not msg:
                    self.shell.print(f"help: {args[1]} does not have a manual or help message")
                else:
                    self.shell.print(f"{args[1]}: {msg}")
            else:
                raise TypeError(f"{args[1]} is not a valid command")
        else:
            self.shell.print(f"bdsh commands:{NL}" + '\t'.join(self.shell.commands.keys()))

    def help(self) -> str:
        return "lists all commands, or displays the help message for individual commands"


class ListDirectoryCommand(Command):
    def execute(self, args: List[str]):
        try:
            path = args[1] if len(args) > 1 else self.shell.path
            items = os.listdir(path)
            self.shell.print(
                '\t'.join([item + '/' if os.path.isdir(os.path.join(path, item)) else item for item in items]))
        except FileNotFoundError:
            raise FileNotFoundError(f"{args[1]}: does not exist")

    def help(self) -> str:
        return "lists the contents of a directory"


class DefineCommand(Command):
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
        return "defines a 'definition', which maps a string to a command"


class ThrowCommand(Command):
    def execute(self, args: List[str]):
        raise Exception(' '.join(args[1:]))

    def help(self) -> str:
        return "throws an exception"


class GoCommand(Command):
    def execute(self, args: List[str]):
        path = self.shell.user_manager.userhome if args[1] == "~" else os.path.join(self.shell.path, args[1])
        if os.path.exists(path):
            self.shell.chdir(path)
        else:
            raise FileNotFoundError(f"{args[1]}: no such file or folder")

    def help(self) -> str:
        return "goes to a directory"


class PeekCommand(Command):
    def execute(self, args: List[str]):
        if os.path.isfile(path := os.path.join(self.shell.path, args[1])):
            with open(path, 'r') as f:
                self.shell.print(f.read())
        else:
            raise FileNotFoundError(f"{args[1]}: no such file")

    def help(self) -> str:
        return "peeks the contents of a file"


def register_commands(shell: Shell) -> Dict[str, Command]:
    return {
        "exit": AnonymousCommand(shell, lambda _: exit(0), ""),
        "help": HelpCommand(shell),
        "echo": AnonymousCommand(shell, lambda args: shell.print(' '.join(args[1:])), ""),
        "ld": ListDirectoryCommand(shell),
        "ver": AnonymousCommand(shell, lambda _: shell.print(shell.header), ""),
        "def": DefineCommand(shell),
        "throw": ThrowCommand(shell),
        "cwd": AnonymousCommand(shell, lambda _: shell.print(shell.cwd()), ""),
        "go": GoCommand(shell),
        "peek": PeekCommand(shell),
        "bpm": BadOSPackageManagerCommand(shell),
        "net": NetCommand(shell),
        "hostname": HostnameCommand(shell),
        "ping": PingCommand(shell)
    }
