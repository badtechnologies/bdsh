from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import List, Any

from bdsh.shell import Shell


class ICommand(ABC):
    @abstractmethod
    def execute(self, args: List[str], shell: Shell):
        pass

    @abstractmethod
    def help(self) -> str:
        pass


class Command(ICommand):
    def __init__(self, execute: Callable[[List[str], Shell], Any], help_msg: str):
        self.help_msg = help_msg
        self.execute = execute

    def execute(self, args: List[str], shell: Shell):
        self.execute(args, shell)

    def help(self) -> str:
        return self.help_msg
