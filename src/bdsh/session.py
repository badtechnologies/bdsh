"""Track user and runtime state for the shell."""

import os
from pathlib import Path

from bdsh import get_shell_path
from bdsh.command.commands import register_commands
from bdsh.io import TerminalIO
from bdsh.service.badlogon import User


class Session:
    """Hold the current user, environment, and shell state."""

    def __init__(self, io: TerminalIO, user: User):
        """Set up a shell session for a user and terminal."""
        if not user:
            raise ValueError("session: cannot create userless session")

        self.__current_user: User | None = None
        self.userhome = None
        self.io = io
        self.cwd = get_shell_path()
        self.is_running = False

        self.env = os.environ.copy()
        self.env['PYTHONPATH'] = str(Path(__file__).resolve().parent)

        self.commands = register_commands(self)
        self.definitions = {
            "ls": "ld",
            "dir": "ld",
            "cd": "go"
        }

        self.set_user(user)

    def is_logged_in(self) -> bool:
        """Return whether a user is logged in."""
        return self.__current_user is not None

    def get_user(self):
        """Return the current user."""
        return self.__current_user

    def set_user(self, user: User):
        """Set the current user and their home directory."""
        self.__current_user = user
        self.userhome = get_shell_path("prf", self.__current_user.username)

    def chdir(self, path: Path):
        """Change the session's current directory."""
        self.cwd = path.resolve()

    def set_is_running(self, is_running: bool):
        """Set whether the shell session is running."""
        self.is_running = is_running
