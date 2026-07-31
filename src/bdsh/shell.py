import os
import subprocess
import sys
from contextlib import redirect_stdout
from typing import TextIO

from bdsh import NL, __version__, get_shell_path, SHELL_COPYRIGHT
from bdsh.command.commands import register_commands
from bdsh.user import User
from bdsh.user.session import SessionManager


class Shell:
    def __init__(self, stdout: TextIO | None, stdin: TextIO | None, user: User, **is_ssh: bool):
        self.stdout = stdout
        self.stdin = stdin
        self.print = lambda s: self.stdout.write(s)
        self.readchar = lambda: self.stdin.read(1)
        self.is_ssh = is_ssh
        self.path = get_shell_path()

        self.header = SHELL_COPYRIGHT

        self.commands = register_commands(self)
        self.definitions = {
            "ls": "ld",
            "dir": "ld",
            "cd": "go"
        }

        self.env = os.environ.copy()
        self.env['PYTHONPATH'] = os.path.dirname(os.path.realpath(__file__))

        self.session = SessionManager(user)

    def fatal(self, msg: str, exit_code: int = 129):
        self.print(f"FATAL({exit_code}): {msg}{NL}")
        exit(exit_code)

    def run_line(self, line: str):
        line = line.strip()  # dont want to process invisible characters

        if line == "":
            return

        args = line.split(' ')

        if args[0] in self.definitions:
            self.run_line(self.definitions[args[0]] + " " + ' '.join(args[1:]))
        elif args[0] in self.commands:
            try:
                with redirect_stdout(self.stdout):
                    self.commands[args[0]].execute(args)
            except Exception as e:
                self.print(f"{args[0]}: {e}")
        elif os.path.exists(binary := get_shell_path("exec", args[0])):
            if self.is_ssh:
                self.print(f"{args[0]} is unsupported over SSH")
                return

            subprocess.run([sys.executable, binary] + args[1:], stdout=self.stdout, stderr=subprocess.STDOUT,
                           stdin=self.stdin, text=True, env=self.env)
        else:
            self.print(f"Invalid command: {args[0]}")

    def cwd(self):
        return self.path

    def chdir(self, path):
        self.path = os.path.abspath(path)

    def get_prompt(self):
        return f"{NL}{self.session.get_user().username}:{"~" if self.path == self.session.userhome else self.cwd()}$ "

    def start(self):
        # ensure session is valid
        os.chdir(self.path)
        self.run_line("ver")

        if not os.path.exists(self.path):
            self.fatal("bdsh: current directory does not exist", 130)

        # handle authentication
        if not self.session.is_logged_in():
            self.fatal("bdsh: attempted to instantiate shell without logging in", 131)

        self.print(f"Welcome, {self.session.get_user().username}!{NL}")
        self.chdir(self.session.userhome)

        # start processing commands
        self.print(self.get_prompt())
        buffer = []

        while True:
            try:
                char = self.readchar()

                if self.is_ssh:
                    self.print(char)

                if char in {'\n', '\r'}:
                    if char == '\r':
                        self.print('\n')
                    self.run_line(''.join(buffer))
                    buffer.clear()
                    self.print(self.get_prompt())
                elif char == '\x03':  # ^C
                    buffer.clear()
                    self.print(self.get_prompt())
                elif char == '\x7f':  # backspace
                    if len(buffer) <= 0:
                        continue
                    self.print('\x08 \x08')
                    buffer.pop()
                else:
                    buffer.append(char)

            except KeyboardInterrupt:
                buffer.clear()
                self.print(self.get_prompt())
                continue

            except Exception as e:
                buffer.clear()
                self.print(f"bdsh: unhandled exception: {e}{NL}{self.get_prompt()}")
                continue
