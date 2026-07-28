import os
import subprocess
import sys
from typing import TextIO

from bdsh import NL
from bdsh.command.commands import register_commands

ROOT_DIR = os.path.abspath('bdsh')


class Shell:
    def __init__(self, stdout: TextIO | None, stdin: TextIO | None, **is_ssh: bool):
        self.stdout = stdout
        self.stdin = stdin
        self.print = lambda s: self.stdout.write(s)
        self.readchar = lambda: self.stdin.read(1)
        self.is_ssh = is_ssh
        self.path = self.get_path()
        self.cwd = lambda: os.path.relpath(self.path, ROOT_DIR).replace('.', '/', 1)

        self.header = f"BadOS Dynamic Shell (v0.1) {'(BadBandSSH)' if is_ssh else ''}{NL}(c) Bad Technologies. All rights reserved.{NL}"

        self.commands = register_commands(self)

        self.definitions = {
            "ls": "ld",
            "dir": "ld",
            "cd": "go"
        }

        self.env = os.environ.copy()
        self.env['PYTHONPATH'] = os.path.dirname(os.path.realpath(__file__))

    def run_line(self, line: str):
        line = line.strip() # dont want to process invisible characters

        if line == "":
            return

        args = line.split(' ')

        if args[0] in self.definitions:
            self.run_line(self.definitions[args[0]] + " " + ' '.join(args[1:]))
        elif args[0] in self.commands:
            try:
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
        path = os.path.abspath(os.path.join(ROOT_DIR, *paths))
        return path if path.startswith(ROOT_DIR) else ROOT_DIR

    def start(self):
        os.chdir(self.get_path())
        self.run_line("ver")

        if not os.path.exists(self.get_path()):
            self.print(f"bdsh: bdsh directory does not exist{NL}")
            exit(1)

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
