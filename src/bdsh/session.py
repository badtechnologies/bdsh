import os

from bdsh import get_shell_path
from bdsh.command.commands import register_commands
from bdsh.io import TerminalIO
from bdsh.user import User


class Session:
    def __init__(self, io: TerminalIO, user: User):
        if not user:
            raise ValueError("session: cannot create userless session")

        self.__current_user = None
        self.userhome = None
        self.io = io
        self.cwd = get_shell_path()

        self.env = os.environ.copy()
        self.env['PYTHONPATH'] = os.path.dirname(os.path.realpath(__file__))

        self.commands = register_commands(self)
        self.definitions = {
            "ls": "ld",
            "dir": "ld",
            "cd": "go"
        }

        self.set_user(user)

    def is_logged_in(self):
        return self.__current_user is not None

    def get_user(self):
        return self.__current_user

    def set_user(self, user: User):
        self.__current_user = user
        self.userhome = get_shell_path("prf", self.__current_user.username)

    def chdir(self, path):
        self.cwd = os.path.abspath(path)
