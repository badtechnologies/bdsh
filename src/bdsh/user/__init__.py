import os
from dataclasses import dataclass
from typing import List, Never

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from bdsh import get_shell_path

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
    def __init__(self, path: str):
        self.path = path
        self.__current_user: User | None = None
        self.home = None

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

                path = get_shell_path("prf", username)
                if not os.path.exists(path):
                    os.mkdir(path)

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

    def login(self, username: str, password: str) -> bool:
        for user in self.users:
            if user.username != username: continue

            result = user.try_login(password)
            if not result: continue

            self.set_current_user(user)
            return True

        return False

    def is_logged_in(self):
        return self.__current_user is not None

    def get_current_user(self):
        return self.__current_user

    def set_current_user(self, user: User):
        self.__current_user = user
        self.home = get_shell_path("prf", self.__current_user.username)