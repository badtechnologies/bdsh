from getpass import getpass

from bdsh import SHELL_COPYRIGHT
from bdsh.service.badlogon import UserManager, User


class BadLoginService:
    def __init__(self):
        self.user_manager = UserManager()

    def shell_login(self) -> User:
        print(SHELL_COPYRIGHT)

        user = None

        while not user:
            try:
                username = input("Username: ")
                password = getpass("Password: ")
                user = self.user_manager.get_user_by_credentials(username, password)
                if not user:
                    print("\nInvalid login")
            except KeyboardInterrupt:
                print()
                continue
        print() # blank line between password field and shell prompt

        return user
