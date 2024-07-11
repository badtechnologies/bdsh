# BadOS Dynamic Shell (bdsh)

import sys

newline = '\r\n'


class Shell:
    def __init__(self, stdout: callable, stdin: callable, **is_ssh: bool):
        self.print = stdout
        self.readchar = stdin
        self.is_ssh = is_ssh

        self.header = f"BadOS Dynamic Shell (v0.1) {'(BadBandSSH)' if is_ssh else ''}{newline}(c) Bad Technologies. All rights reserved.{newline}"

        self.commands = {
            "exit": lambda args: exit(0),
            "help": lambda args: self.print("haha no")
        }

    def run_line(self, line: str):
        args = line.lower().split(' ')

        if args[0] in self.commands:
            self.commands[args[0]](args)
        else:
            self.print(f"Invalid command: {args[0]}")

    def get_prompt(self):
        return f"{newline}$ "

    def start(self):
        self.print(self.header)
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
                elif char == '\x03':
                    buffer.clear()
                    self.print(self.get_prompt())
                else:
                    buffer.append(char)

            except KeyboardInterrupt:
                buffer.clear()
                self.print(self.get_prompt())
                continue


if __name__ == "__main__":
    bdsh = Shell(sys.stdout.write, lambda: sys.stdin.read(1))
    bdsh.start()
