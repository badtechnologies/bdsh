import os
import subprocess
import sys
from contextlib import redirect_stdout
from getpass import getpass
from typing import TextIO

from bdsh import NL, __version__, get_shell_path, ROOT_DIR
from bdsh.command.commands import register_commands
from bdsh.user import User, UserManager


class Shell:
    def __init__(self, stdout: TextIO | None, stdin: TextIO | None, **is_ssh: bool):
        self.stdout = stdout
        self.stdin = stdin
        self.print = lambda s: self.stdout.write(s)
        self.readchar = lambda: self.stdin.read(1)
        self.is_ssh = is_ssh
        self.path = Shell.get_path()
        self.cwd = lambda: os.path.relpath(self.path, ROOT_DIR).replace('.', '/', 1)

        self.header = f"BadOS Dynamic Shell (v{__version__}) {'(BadBandSSH)' if is_ssh else ''}{NL}(c) Bad Technologies. All rights reserved.{NL}"

        self.commands = register_commands(self)
        self.definitions = {
            "ls": "ld",
            "dir": "ld",
            "cd": "go"
        }

        self.env = os.environ.copy()
        self.env['PYTHONPATH'] = os.path.dirname(os.path.realpath(__file__))

        self.user_manager = UserManager(Shell.get_path("cfg", "userman"))

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
        elif os.path.exists(binary := self.get_path("exec", args[0])):
            if self.is_ssh:
                self.print(f"{args[0]} is unsupported over SSH")
                return

            subprocess.run([sys.executable, binary] + args[1:], stdout=self.stdout, stderr=subprocess.STDOUT,
                           stdin=self.stdin, text=True, env=self.env)
        else:
            self.print(f"Invalid command: {args[0]}")

    def get_prompt(self):
        return f"{NL}{self.cwd()}$ "

    @staticmethod
    def get_path(*paths: str):
        return get_shell_path(*paths)

    def start(self):
        # ensure session is valid
        os.chdir(self.get_path())
        self.run_line("ver")

        if not os.path.exists(self.get_path()):
            self.print(f"bdsh: bdsh directory does not exist{NL}")
            exit(1)

        # handle authentication
        if not self.user_manager.is_logged_in():
            self.print(NL + "You are not logged in!" + NL)

        while not self.user_manager.is_logged_in():
            try:
                username = input("Username: ")
                password = getpass("Password: ")
                success = self.user_manager.login(username, password)
                if not success:
                    self.print(NL + "Invalid login" + NL)
            except KeyboardInterrupt:
                self.print(NL)
                continue

        self.print(f"Welcome, {self.user_manager.get_current_user().username}!{NL}")

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
