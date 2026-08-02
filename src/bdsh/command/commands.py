from typing import List, Dict, TYPE_CHECKING

from bdsh import NL, SHELL_COPYRIGHT
from bdsh.command import Command, AnonymousCommand
from bdsh.command.bpm import BadOSPackageManagerCommand
from bdsh.command.net import NetCommand, HostnameCommand, PingCommand

if TYPE_CHECKING:
    from bdsh.session import Session


class HelpCommand(Command):
    def execute(self, args: List[str]):
        if len(args) > 1:
            subcommand = self.session.commands.get(args[1])
            if isinstance(subcommand, Command):
                msg = subcommand.help()

                if not msg:
                    self.session.io.println(f"help: {args[1]} does not have a manual or help message")
                else:
                    self.session.io.println(f"help: {args[1]}: {msg}")
            else:
                raise TypeError(f"{args[1]} is not a valid command")
        else:
            self.session.io.println(f"bdsh commands:{NL}" + '\t'.join(self.session.commands.keys()))

    def help(self) -> str:
        return "lists all commands, or displays the help message for individual commands"


class ListDirectoryCommand(Command):
    def execute(self, args: List[str]):
        try:
            path = self.session.cwd.joinpath(args[1]).resolve() if len(args) > 1 else self.session.cwd

            self.session.io.println('\t'.join([
                str(item.name) + '/' if path.joinpath(item).is_dir() else str(item.name)
                for item in path.iterdir()
            ]))
        except FileNotFoundError:
            raise FileNotFoundError(f"{args[1]}: does not exist")

    def help(self) -> str:
        return "lists the contents of a directory"


class DefineCommand(Command):
    def execute(self, args: List[str]):
        if len(args) < 3:
            raise ValueError("missing params (at least 3)")

        definition = " ".join(args[2:])

        if args[1] == definition:
            raise ValueError("keyword cannot be the same as the definition")

        self.session.definitions[args[1]] = definition
        self.session.io.println(f"defined '{args[1]}' to run '{definition}'")

    def help(self) -> str:
        return f"usage: def <keyword> <definition>{NL}binds <keyword> to <definition>{NL}executing <keyword> will execute <definition>"


class ThrowCommand(Command):
    def execute(self, args: List[str]):
        raise Exception(' '.join(args[1:]))

    def help(self) -> str:
        return "throws an exception"


class GoCommand(Command):
    def execute(self, args: List[str]):
        path = self.session.userhome if args[1] == "~" else self.session.cwd.joinpath(args[1])
        if path.is_dir():
            self.session.chdir(path)
        else:
            raise FileNotFoundError(f"{args[1]}: no such folder")

    def help(self) -> str:
        return "goes to a directory"


class PeekCommand(Command):
    def execute(self, args: List[str]):
        path = self.session.cwd.joinpath(args[1])
        if path.is_file(follow_symlinks=True):
            with open(path, 'r') as f:
                self.session.io.println(f.read())
        else:
            raise FileNotFoundError(f"{args[1]}: no such file")

    def help(self) -> str:
        return "peeks the contents of a file"


def register_commands(session: Session) -> Dict[str, Command]:
    return {
        "exit": AnonymousCommand(session, lambda _: exit(0), ""),
        "help": HelpCommand(session),
        "echo": AnonymousCommand(session, lambda args: session.io.println(' '.join(args[1:])), ""),
        "ld": ListDirectoryCommand(session),
        "ver": AnonymousCommand(session, lambda _: session.io.println(SHELL_COPYRIGHT), ""),
        "def": DefineCommand(session),
        "throw": ThrowCommand(session),
        "cwd": AnonymousCommand(session, lambda _: session.io.println(session.cwd), ""),
        "go": GoCommand(session),
        "peek": PeekCommand(session),
        "bpm": BadOSPackageManagerCommand(session),
        "net": NetCommand(session),
        "hostname": HostnameCommand(session),
        "ping": PingCommand(session)
    }
