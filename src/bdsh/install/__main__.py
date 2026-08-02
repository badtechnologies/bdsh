import subprocess
import sys
from getpass import getpass

from bdsh import OSPaths, SHELL_COPYRIGHT
from bdsh.install import InstallType
from bdsh.install.util import prompt, print_header, print_task, install_python_package
from bdsh.io.console import ConsoleTerminal
from bdsh.session import Session
from bdsh.shell import Shell
from bdsh.user import UserManager, User

PYREQS_URL = "https://raw.githubusercontent.com/badtechnologies/bdsh/main/requirements.txt"
GIT_URL = "https://github.com/badtechnologies/bdsh"
BDSH_SRC_URL = "https://raw.githubusercontent.com/badtechnologies/bdsh/main/bdsh.py"
BPL_URL = "https://raw.githubusercontent.com/badtechnologies/bpl/main/lib"

PYREQS = "requirements.txt"
BDSH_SRC = "src/bdsh/bdsh.py"

BDSH_ROOT = OSPaths.ROOT


def main():
    # default args
    install_type = InstallType.STANDARD

    # parse args
    for arg in sys.argv:
        arg = arg.split("=")
        if len(arg) < 1:
            continue
        if arg[0] == "type":
            try:
                install_type = InstallType(arg[1])
            except ValueError as e:
                print(f"{e}, choose from:")
                InstallType.display()
                exit()

    print(f"BDSH INSTALLATION TOOL, {install_type.name} INSTALL\n(c) Bad Technologies. All rights reserved.\n")
    if install_type is not InstallType.SYSTEM and BDSH_ROOT.exists():
        prompt("This will replace your current bdsh configs, proceed?", lambda: exit(0))

    print_header("SETUP ENV")

    if install_type is not InstallType.SYSTEM:
        print_task("Upgrading environment package installer")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("OK")
        except subprocess.CalledProcessError:
            print("FAILED")

    print_task("Installing system HTTP client")
    install_python_package("requests")

    print_header("INIT BDSH")

    print_task("Initializing bdsh directory structure")
    try:
        BDSH_ROOT.mkdir(exist_ok=True)

        for path in OSPaths.all():
            path.mkdir(exist_ok=True)

        print("OK")
    except Exception as e:
        print(f"FAILED\n{e}")
        exit(0x84)

    if install_type is not InstallType.SYSTEM:
        print(f"Populated bdsh root ({BDSH_ROOT}/) successfully")

    print("Starting virtual bdsh session")
    virtsh = Shell(Session(ConsoleTerminal(), User("VirtualInstaller", "")))
    print(SHELL_COPYRIGHT)

    print_header("CREATE USERS")

    userman = UserManager(OSPaths.CONFIGS.joinpath("userman"))
    while True:
        username = input("Enter username\t\t")
        password = getpass("Enter password\t\t")

        try:
            userman.add(username, password)
        except ValueError as e:
            print(f"Failed to create user: {e}. Try again.")
            continue

        def exit_loop():
            nonlocal username
            username = None

        prompt("Create another?", exit_loop)

        if username is None:
            break

    print_task("Create users")
    userman.save()
    print("OK")

    print_header("INSTALL PACKAGES")
    virtsh.run_line("bpm install -y core")


if __name__ == "__main__":
    main()
