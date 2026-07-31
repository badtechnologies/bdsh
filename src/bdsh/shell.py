import os
import subprocess
import sys

from bdsh import NL, get_shell_path
from bdsh.session import Session


class Shell:
    def __init__(self, session: Session):
        self.session = session

    def fatal(self, msg: str, exit_code: int = 129):
        self.session.io.println(f"FATAL({exit_code}): {msg}")
        exit(exit_code)

    def run_line(self, line: str):
        line = line.strip()  # dont want to process invisible characters

        if line == "":
            return

        args = line.split(' ')

        if args[0] in self.session.definitions:
            self.run_line(self.session.definitions[args[0]] + " " + ' '.join(args[1:]))
        elif args[0] in self.session.commands:
            try:
                self.session.commands[args[0]].execute(args)
            except Exception as e:
                self.session.io.print(f"{args[0]}: {e}")
        elif os.path.exists(binary := get_shell_path("exec", args[0])):
            subprocess.run([sys.executable, binary] + args[1:], stdout=self.stdout, stderr=subprocess.STDOUT,
                           stdin=self.stdin, text=True, env=self.session.env)
        else:
            self.session.io.println(f"invalid command: {args[0]}")

    def get_prompt(self):
        return f"{NL}{self.session.get_user().username}:{"~" if self.session.cwd == self.session.userhome else self.session.cwd}$ "

    def start(self):
        # ensure session is valid
        os.chdir(self.session.cwd)
        self.run_line("ver")

        if not os.path.exists(self.session.cwd):
            self.fatal("bdsh: current directory does not exist", 130)

        # handle authentication
        if not self.session.is_logged_in():
            self.fatal("bdsh: attempted to instantiate shell without logging in", 131)

        self.session.io.println(f"Welcome, {self.session.get_user().username}!")
        self.session.chdir(self.session.userhome)

        # start processing commands
        self.session.io.print(self.get_prompt())
        buffer = []

        while True:
            try:
                char = self.session.io.read(1)

                if char in {'\n', '\r'}:
                    if char == '\r':
                        self.session.io.print('\n')
                    self.run_line(''.join(buffer))
                    buffer.clear()
                    self.session.io.print(self.get_prompt())
                elif char == '\x03':  # ^C
                    buffer.clear()
                    self.session.io.print(self.get_prompt())
                elif char == '\x7f':  # backspace
                    if len(buffer) <= 0:
                        continue
                    self.session.io.print('\x08 \x08')
                    buffer.pop()
                else:
                    buffer.append(char)

            except KeyboardInterrupt:
                buffer.clear()
                self.session.io.print(self.get_prompt())
                continue

            except Exception as e:
                buffer.clear()
                self.session.io.print(f"bdsh: unhandled exception: {e}{NL}{self.get_prompt()}")
                continue
