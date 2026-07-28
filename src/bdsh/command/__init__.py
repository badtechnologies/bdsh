from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from bdsh.shell import Shell


class Command(ABC):
    def __init__(self, shell: Shell):
        self.shell = shell

    @abstractmethod
    def execute(self, args: List[str]):
        pass

    @abstractmethod
    def help(self) -> str:
        pass


class AnonymousCommand(Command):
    def __init__(self, shell: Shell, execute: Callable[[List[str]], Any], help_msg: str):
        super().__init__(shell)
        self.help_msg = help_msg
        self.execute = execute

    def execute(self, args: List[str]):
        self.execute(args)

    def help(self) -> str:
        return self.help_msg
