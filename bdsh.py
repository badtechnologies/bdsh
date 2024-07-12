# BadOS Dynamic Shell (bdsh)

import sys
import os
import subprocess

newline = '\r\n'
root_dir = os.path.abspath('bdsh')


class Shell:
    def __init__(self, stdout: callable, stdin: callable, **is_ssh: bool):
        self.print = stdout
        self.readchar = stdin
        self.is_ssh = is_ssh

        self.header = f"BadOS Dynamic Shell (v0.1) {'(BadBandSSH)' if is_ssh else ''}{newline}(c) Bad Technologies. All rights reserved.{newline}"

        self.commands = {
            "exit": lambda _: exit(0),
            "help": lambda _: self.print("haha no"),
            "echo": lambda args: self.print(' '.join(args[1:])),
            "ld": self.cmd_ld,
        }

    def cmd_ld(self, args):
        try:
            self.print('\t'.join([item + '/' if os.path.isdir(os.path.join(self.get_path(args[1] if len(args) > 1 else ""), item)) else item for item in os.listdir(self.get_path(args[1] if len(args) > 1 else ""))]))
        except FileNotFoundError:
            self.print(f"{args[0]}: {args[1]}: does not exist")

    def run_line(self, line: str):
        if line == "":
            return

        args = line.split(' ')

        if args[0] in self.commands:
            try:
                self.commands[args[0].lower()](args)
            except Exception as e:
                self.print(f"{args[0]}: {e}")
        elif os.path.exists(bin := self.get_path("exec", args[0])):
            subprocess.run([sys.executable, bin] + args[1:], stdout=sys.stdout, stderr=subprocess.STDOUT, text=True)
        else:
            self.print(f"Invalid command: {args[0]}")

    def get_prompt(self):
        return f"{newline}$ "
    
    def get_path(self, *paths: str):
        dir = os.path.abspath(os.path.join(root_dir, *paths))
        return dir if dir.startswith(root_dir) else root_dir

    def start(self):
        self.print(self.header)

        if not os.path.exists(self.get_path()):
            self.print(f"bdsh: bdsh directory does not exist{newline}")
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
                elif char == '\x03':    # ^C
                    buffer.clear()
                    self.print(self.get_prompt())
                elif char == '\x7f':    # backspace
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


if __name__ == "__main__":
    bdsh = Shell(sys.stdout.write, lambda: sys.stdin.read(1))
    bdsh.start()
