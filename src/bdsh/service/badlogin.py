from getpass import getpass

from bdsh import get_shell_path
from bdsh.user import UserManager, User


def shell_login(std) -> User:
    user_manager = UserManager(get_shell_path("cfg", "userman"))
    user = None

    while not user:
        try:
            username = input("Username: ")
            password = getpass("Password: ")
            user = user_manager.get_user_by_credentials(username, password)
            if not user:
                print("\nInvalid login")
        except KeyboardInterrupt:
            print()
            continue

    return user
