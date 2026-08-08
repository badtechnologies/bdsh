from dataclasses import dataclass
from pathlib import Path
from typing import List, Never

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from bdsh import OSPaths
from bdsh.service.rpc import RPCSocketService, RPCSocketClient, servicemethod

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


class BadLogonService(RPCSocketService, name="badlogon.badproc"):
    def __init__(self, userman_path: Path = OSPaths.CONFIGS.joinpath("userman")):
        super().__init__()
        self.path = userman_path

        try:
            self.users = self.load()
        except FileNotFoundError:
            self.users = []
            self.save()

    @servicemethod
    def save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            for user in self.users:
                f.write(f"{user.username}:{user.password_hash}\n")

    @servicemethod
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

    @servicemethod
    def validate_username(self, username: str) -> bool:
        return not (':' in username)

    @servicemethod
    def add(self, username: str, password: str) -> None:
        if not self.validate_username(username):
            raise ValueError("username contains illegal characters")

        if username.strip() == '' or password.strip() == '':
            raise ValueError("username or password cannot be empty")

        for user in self.users:
            if user.username == username:
                raise ValueError("username already in use")

        self.users.append(User(username, hasher.hash(password)))

    @servicemethod
    def get_user_by_credentials(self, username: str, password: str) -> User | None:
        for user in self.users:
            if user.username != username: continue

            result = user.try_login(password)
            if not result: continue

            return user

        return None


class BadLogonClient(RPCSocketClient):
    def __init__(self):
        super().__init__("badlogon.badproc")
