import os
import sys

from bdsh.io import TerminalIO


class ConsoleTerminal(TerminalIO):
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