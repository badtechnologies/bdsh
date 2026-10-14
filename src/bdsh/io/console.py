from contextlib import contextmanager
import os
import sys
from collections.abc import Iterator

from bdsh.io import TerminalIO


class ConsoleTerminal(TerminalIO):
    @contextmanager
    def interactive_mode(self) -> Iterator[None]:
        if os.name != "posix" or not self.is_interactive():
            yield
            return

        import termios
        import tty

        fd = sys.stdin.fileno()
        original = termios.tcgetattr(fd)
        tty.setcbreak(fd)
        try:
            yield
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, original)

    def read(self, size=-1):
        return sys.stdin.read(size)

    def readline(self):
        return input()

    def write(self, text):
        sys.stdout.write(text)

    def flush(self):
        sys.stdout.flush()

    def close(self):
        sys.stdout.close()
        sys.stdin.close()

    def get_size(self):
        return os.get_terminal_size()

    def is_interactive(self):
        return sys.stdin.isatty() and sys.stdout.isatty()