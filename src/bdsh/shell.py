import os
import subprocess
import sys
from typing import TextIO

from bdsh.command import Command

nl = '\r\n'
root_dir = os.path.abspath('bdsh')


class Shell:
    def __init__(self, stdout: TextIO | None, stdin: TextIO | None, **is_ssh: bool):
        self.stdout = stdout
        self.stdin = stdin
        self.print = lambda s: self.stdout.write(s)
        self.readchar = lambda: self.stdin.read(1)
        self.is_ssh = is_ssh
        self.path = self.get_path()
        self.cwd = lambda: os.path.relpath(self.path, root_dir).replace('.', '/', 1)

        self.header = f"BadOS Dynamic Shell (v0.1) {'(BadBandSSH)' if is_ssh else ''}{nl}(c) Bad Technologies. All rights reserved.{nl}"

        self.commands = {
            "exit": Command(lambda _: exit(0), ""),
            "help": Command(lambda _: self.print(f"bdsh commands:{nl}" + '\t'.join(self.commands.keys())), ""),
            "echo": Command(lambda args: self.print(' '.join(args[1:])), ""),
            "ld": Command(self.cmd_ld, ""),
            "ver": Command(lambda _: self.print(self.header), ""),
            "def": Command(self.cmd_def, ""),
            "throw": Command(self.cmd_throw, ""),
            "cwd": Command(lambda _: self.print(self.cwd()), ""),
            "go": Command(self.cmd_go, ""),
            "peek": Command(self.cmd_peek, ""),
        }

        self.definitions = {
            "ls": "ld",
            "dir": "ld",
            "cd": "go"
        }

        self.env = os.environ.copy()
        self.env['PYTHONPATH'] = os.path.dirname(os.path.realpath(__file__))

    def cmd_ld(self, args):
        try:
            path = self.get_path(args[1]) if len(args) > 1 else self.path
            items = os.listdir(path)
            self.print('\t'.join([item + '/' if os.path.isdir(os.path.join(path, item)) else item for item in items]))
        except FileNotFoundError:
            raise FileNotFoundError(f"{args[1]}: does not exist")

    def cmd_def(self, args):
        if '-h' in args or '--help' in args:
            self.print(
                f"usage: def <keyword> <definition>{nl}binds <keyword> to <definition>{nl}executing <keyword> will execute <definition>")
            return

        if len(args) < 3:
            raise ValueError("missing params (at least 3)")

        definition = " ".join(args[2:])

        if args[1] == definition:
            raise SyntaxError("keyword cannot be the same as the definition")

        self.definitions[args[1]] = definition
        self.print(f"defined '{args[1]}' to run '{definition}'")

    def cmd_throw(self, args):
        raise Exception(' '.join(args[1:]))

    def cmd_go(self, args):
        if os.path.exists(path := self.get_path(args[1])):
            self.path = path
            os.chdir(path)
        else:
            raise FileNotFoundError(f"{args[1]}: no such file or folder")

    def cmd_peek(self, args):
        if os.path.isfile(path := os.path.join(self.path, args[1])):
            with open(path, 'r') as f:
                self.print(f.read())
        else:
            raise FileNotFoundError(f"{args[1]}: no such file")

    def run_line(self, line: str):
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
        return f"{nl}{self.cwd()}$ "

    @staticmethod
    def get_path(*paths: str):
        path = os.path.abspath(os.path.join(root_dir, *paths))
        return path if path.startswith(root_dir) else root_dir

    def start(self):
        os.chdir(self.get_path())
        self.run_line("ver")

        if not os.path.exists(self.get_path()):
            self.print(f"bdsh: bdsh directory does not exist{nl}")
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
                self.print(f"bdsh: unhandled exception: {e}{nl}{self.get_prompt()}")
                continue
