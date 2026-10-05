from dataclasses import dataclass
from pathlib import Path
from typing import Never, Protocol, TypedDict

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from bdsh import OSPaths
from bdsh.service.rpc import RPCSocketService, servicemethod

hasher = PasswordHasher()


class SerializedUser(TypedDict):
    username: str
    password_hash: str


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


class BadLogonAPI(Protocol):
    def save(self) -> None: ...

    def load(self) -> list[SerializedUser]: ...

    def add(self, *, username: str, password: str) -> None: ...

    def get_user_by_credentials(self, *, username: str, password: str) -> SerializedUser | None: ...

    def validate_username(self, *, username: str) -> bool: ...


class BadLogonService(RPCSocketService, BadLogonAPI, name="badlogon.sys"):
    def __init__(self, userman_path: Path = OSPaths.CONFIGS.joinpath("userman")):
        super().__init__()
        self.path = userman_path

        try:
            self.users = [User(**usr) for usr in self.load()]
        except FileNotFoundError:
            self.users = []
            self.save()

    @servicemethod
    def save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            for user in self.users:
                f.write(f"{user.username}:{user.password_hash}\n")

    @servicemethod
    def load(self) -> list[SerializedUser] | Never:
        users: list[SerializedUser] = []

        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")

                if not line:
                    continue

                a, b = line.split(":", 1)
                users.append(SerializedUser(username=a, password_hash=b))

                OSPaths.PROFILES.joinpath(a).mkdir(exist_ok=True)

        return users

    @servicemethod
    def validate_username(self, *, username: str) -> bool:
        return not (':' in username)

    @servicemethod
    def add(self, *, username: str, password: str) -> None:
        if not self.validate_username(username=username):
            raise ValueError("username contains illegal characters")

        if username.strip() == '' or password.strip() == '':
            raise ValueError("username or password cannot be empty")

        for user in self.users:
            if user.username == username:
                raise ValueError("username already in use")

        self.users.append(User(username, hasher.hash(password)))

    @servicemethod
    def get_user_by_credentials(self, *, username: str, password: str) -> SerializedUser | None:
        for user in self.users:
            if user.username != username: continue

            result = user.try_login(password)
            if not result: continue

            return SerializedUser(username=user.username, password_hash=user.password_hash)

        return None
