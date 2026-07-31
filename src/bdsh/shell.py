import os
import subprocess
import sys

from bdsh import NL, get_shell_path, SHELL_COPYRIGHT
from bdsh.command.commands import register_commands
from bdsh.session import Session


class Shell:
    def __init__(self, session: Session):
        self.session = session
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

    def fatal(self, msg: str, exit_code: int = 129):
        self.session.io.println(f"FATAL({exit_code}): {msg}")
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
                self.commands[args[0]].execute(args)
            except Exception as e:
                self.session.io.print(f"{args[0]}: {e}")
        elif os.path.exists(binary := get_shell_path("exec", args[0])):
            subprocess.run([sys.executable, binary] + args[1:], stdout=self.stdout, stderr=subprocess.STDOUT,
                           stdin=self.stdin, text=True, env=self.env)
        else:
            self.session.io.println(f"invalid command: {args[0]}")

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

        self.session.io.println(f"Welcome, {self.session.get_user().username}!")
        self.chdir(self.session.userhome)

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
