"""Minimal standard-library-only shell profile for use as PID 1."""

import cmd
import os
import shlex
import signal
import threading
from pathlib import Path
from typing import TextIO


_CHILD_EVENT = threading.Event()


def reap_children(signum: int, frame: object) -> None:
    """Reap every terminated child process after SIGCHLD."""
    while True:
        try:
            pid, _ = os.waitpid(-1, os.WNOHANG)
        except ChildProcessError:
            break
        if pid == 0:
            break
    _CHILD_EVENT.set()


class BootShell(cmd.Cmd):
    """Small shell with built-ins that use only the Python standard library."""

    prompt = "bdsh# "

    def __init__(self, stdin: TextIO | None = None, stdout: TextIO | None = None):
        super().__init__(stdin=stdin, stdout=stdout)
        self.cwd = Path("/")

    def _path(self, value: str) -> Path:
        path = Path(value)
        if not path.is_absolute():
            path = self.cwd / path
        return path.resolve(strict=True)

    def do_pwd(self, argument: str) -> None:
        """Print the shell's current directory."""
        print(self.cwd, file=self.stdout)

    def do_checkpid(self, argument: str) -> None:
        """Print the process ID running the init shell."""
        print(os.getpid(), file=self.stdout)

    def do_ls(self, argument: str) -> None:
        """List a directory, defaulting to the shell's current directory."""
        try:
            args = shlex.split(argument)
            if len(args) > 1:
                raise ValueError("usage: ls [directory]")
            path = self._path(args[0]) if args else self.cwd
            if not path.is_dir():
                raise NotADirectoryError(path)
            for entry in sorted(path.iterdir()):
                print(entry.name + ("/" if entry.is_dir() else ""), file=self.stdout)
        except (OSError, ValueError) as error:
            print(f"ls: {error}", file=self.stdout)

    def do_cd(self, argument: str) -> None:
        """Change the shell's current directory; no argument returns to /."""
        try:
            args = shlex.split(argument)
            if len(args) > 1:
                raise ValueError("usage: cd [directory]")
            path = self._path(args[0]) if args else Path("/")
            if not path.is_dir():
                raise NotADirectoryError(path)
            self.cwd = path
        except (OSError, ValueError) as error:
            print(f"cd: {error}", file=self.stdout)

    def do_cat(self, argument: str) -> None:
        """Print one or more files."""
        try:
            paths = shlex.split(argument)
            if not paths:
                raise ValueError("usage: cat file [...]")
            for value in paths:
                print(self._path(value).read_text(), end="", file=self.stdout)
        except (OSError, ValueError) as error:
            print(f"cat: {error}", file=self.stdout)

    def do_echo(self, argument: str) -> None:
        """Print its arguments."""
        print(argument, file=self.stdout)

    def do_exit(self, argument: str) -> bool:
        """Keep PID 1 alive; exit is not available in the boot profile."""
        print("bdsh-init: exit is disabled while running as init", file=self.stdout)
        return False

    do_quit = do_exit

    def do_EOF(self, argument: str) -> bool:
        """Wait for a child-process signal rather than exiting as PID 1."""
        print("\nbdsh-init: input closed; waiting for a child-process signal", file=self.stdout)
        return True


def main() -> None:
    """Run the boot shell and keep the init process alive."""
    signal.signal(signal.SIGCHLD, reap_children)
    shell = BootShell()
    while True:
        _CHILD_EVENT.clear()
        shell.cmdloop()
        _CHILD_EVENT.wait()


if __name__ == "__main__":
    main()
