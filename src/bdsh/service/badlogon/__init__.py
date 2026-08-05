from dataclasses import dataclass
from pathlib import Path
from typing import List, Never

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from bdsh import OSPaths
from bdsh.service.ipc import IPCSocketService

hasher = PasswordHasher()


@dataclass
class User:
    username: str
    password_hash: str

    def try_login(self, password: str) -> bool:
        try:
            hasher.verify(self.password_hash, password)
            return True
        except VerifyMismatchError:
            return False


class UserManager:
    def __init__(self, userman_path: Path = OSPaths.CONFIGS.joinpath("userman")):
        self.path = userman_path

        try:
            self.users = self.load()
        except FileNotFoundError:
            self.users = []
            self.save()

    def save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            for user in self.users:
                f.write(f"{user.username}:{user.password_hash}\n")

    def load(self) -> List[User] | Never:
        users = []

        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")

                if not line:
                    continue

                username, password_hash = line.split(":", 1)
                users.append(User(username, password_hash))

                OSPaths.PROFILES.joinpath(username).mkdir(exist_ok=True)

        return users

    @staticmethod
    def validate_username(username: str) -> bool:
        return not (':' in username)

    def add(self, username: str, password: str) -> None:
        if not UserManager.validate_username(username):
            raise ValueError("username contains illegal characters")

        if username.strip() == '' or password.strip() == '':
            raise ValueError("username or password cannot be empty")

        for user in self.users:
            if user.username == username:
                raise ValueError("username already in use")

        self.users.append(User(username, hasher.hash(password)))

    def get_user_by_credentials(self, username: str, password: str) -> User | None:
        for user in self.users:
            if user.username != username: continue

            result = user.try_login(password)
            if not result: continue

            return user

        return None


class BadLogonService(IPCSocketService, name="badlogon.badproc"):
    def dispatch(self, method, params):
        user_manager = UserManager()

        match method:
            case "save":
                return user_manager.save()
            case "load":
                return user_manager.load()
            case "add":
                return user_manager.add(params["username"], params["password"])
            case "get_user_by_credentials":
                return user_manager.get_user_by_credentials(params["username"], params["password"])
            case "validate_username":
                return user_manager.validate_username(params["username"])
            case _:
                raise ValueError(f"unknown method: '{method}'")
