import os
import os
import subprocess
import sys
from getpass import getpass

from bdsh.install import InstallType
from bdsh.install.util import prompt, print_header, print_task, install_package
from bdsh.security.users import UserManager
from bdsh.shell import Shell

PYREQS_URL = "https://raw.githubusercontent.com/badtechnologies/bdsh/main/requirements.txt"
GIT_URL = "https://github.com/badtechnologies/bdsh"
BDSH_SRC_URL = "https://raw.githubusercontent.com/badtechnologies/bdsh/main/bdsh.py"
BPL_URL = "https://raw.githubusercontent.com/badtechnologies/bpl/main/lib"

PYREQS = "requirements.txt"
BDSH_SRC = "src/bdsh/bdsh.py"

BDSH_DIRS = ['cfg', 'prf', 'exec']
BDSH_ROOT = "bdsh"


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
    if install_type is not InstallType.SYSTEM and os.path.exists(BDSH_ROOT):
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
    install_package("requests")

    print_task("Installing security manager")
    install_package("requests")
    from paramiko import RSAKey

    print_header("INIT BDSH")

    print_task("Initializing bdsh directory structure")
    try:
        if not os.path.exists(BDSH_ROOT):
            os.mkdir(BDSH_ROOT)

        for dir in BDSH_DIRS:
            path = os.path.join(BDSH_ROOT, dir)
            if not os.path.exists(path):
                os.mkdir(path)

        print("OK")
    except Exception as e:
        print(f"FAILED\n{e}")
        exit(0x84)

    if install_type is not InstallType.SYSTEM:
        print(f"Populated bdsh root ({BDSH_ROOT}/) successfully")

    print("Starting virtual bdsh session")
    virtsh = Shell(sys.stdout, sys.stdin)
    print(Shell(None, None).header)

    print_header("CREATE USERS")

    userman = UserManager(os.path.join(BDSH_ROOT, "cfg", "userman"))
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

    print_header("SETUP BADBANDSSH")

    key = RSAKey.generate(bits=2048)
    key.write_private_key_file(virtsh.get_path('cfg', 'badbandssh_rsa_key'))
    print("Stored BadBandSSH private key")


if __name__ == "__main__":
    main()
