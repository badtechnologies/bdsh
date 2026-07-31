import inspect
import os

from bdsh import NL
from bdsh.session import Session
from bdsh.util.exec import load_exec, get_exec_path


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
        elif os.path.exists(path := get_exec_path(args[0])):
            module = load_exec(path)
            if hasattr(module, "main"):
                module.main(session=self.session, args=args[1:])

                sig = inspect.signature(module.main)
                params = list(sig.parameters.values())

                if len(params) != 2:
                    self.session.io.println(f"{args[0]}: main() must accept exactly (session, args)")
            else:
                self.session.io.println(f"{args[0]}: no main() function found")
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
