from dataclasses import dataclass
from typing import List, Never

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

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
    def __init__(self, path):
        try:
            self.users = UserManager.load(path)
        except FileNotFoundError:
            UserManager.save(path, [])
            self.users = []

    @staticmethod
    def save(path: str, users: List[User]) -> None:
        with open(path, "w", encoding="utf-8") as f:
            for user in users:
                f.write(f"{user.username}:{user.password_hash}\n")

    @staticmethod
    def load(path: str) -> List[User] | Never:
        users = []

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")

                if not line:
                    continue

                username, password_hash = line.split(":", 1)
                users.append(User(username, password_hash))

        return users

    @staticmethod
    def validate_username(username: str) -> bool:
        return not (':' in username)

    def add(self, username: str, password: str) -> None:
        if not UserManager.validate_username(username):
            raise ValueError("username contains illegal characters")

        self.users.append(User(username, hasher.hash(password)))

    def try_login(self, username: str, password: str) -> User | None:
        for user in self.users:
            if user.username != username: continue

            result = user.try_login(password)
            if not result: continue

            return user

        return None
