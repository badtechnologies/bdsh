from abc import ABC, abstractmethod

from bdsh import NL


class TerminalIO(ABC):
    @abstractmethod
    def read(self, size: int = -1) -> str:
        ...

    @abstractmethod
    def readline(self) -> str:
        ...

    @abstractmethod
    def write(self, text: str):
        ...

    @abstractmethod
    def flush(self):
        ...

    @abstractmethod
    def close(self):
        ...

    @abstractmethod
    def get_size(self):
        ...

    @abstractmethod
    def is_interactive(self):
        ...

    def print(self, text):
        self.write(text)
        self.flush()

    def println(self, text=""):
        self.write(text + NL)
        self.flush()

    def clear(self):
        if not self.is_interactive(): return

        self.write("\033[H\033[2J")
        self.flush()

    def bell(self):
        self.write("\a")
        self.flush()

    def set_title(self, title):
        if not self.is_interactive(): return

        self.write(f"\033]0;{title}\007")
        self.flush()

    def input(self, prompt: str = ""):
        self.print(prompt)
        return self.readline()
