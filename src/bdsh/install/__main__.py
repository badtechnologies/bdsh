import json
import os
import subprocess
import sys
from getpass import getpass

from bdsh.install import InstallType
from bdsh.install.util import prompt, print_header, print_task, install_package

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
    import requests

    print_task("Installing security manager")
    install_package("requests")
    from paramiko import RSAKey

    print_task("Installing BadOS Dynamic Shell")
    install_package("bdsh")
    from bdsh.shell import Shell

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

    users = {}
    while True:
        username = input("Enter username\t\t")
        password = getpass("Enter password\t\t")

        if username.strip() == '' or password.strip() == '':
            print("Empty username or password, try again")
            continue

        if username in users:
            print("Username in use, try again")
            continue

        users[username] = password

        def exit_loop():
            nonlocal username
            username = None

        prompt("Create another?", exit_loop)

        if username is None:
            break

    with open(f'{BDSH_ROOT}/cfg/users.json', 'w') as f:
        json.dump(users, f)

    for username in users.keys():
        path = os.path.join(f'{BDSH_ROOT}/prf', username)
        if not os.path.exists(path):
            os.mkdir(path)

    print(f"Created {len(users)} user(s)")

    print_header("INSTALL BPM")

    install_packages = True
    def stop_install():
        nonlocal install_packages
        install_packages = False

    res = None
    while install_packages:
        print_task("Fetching bpm from bpl")
        res = requests.get(f'{BPL_URL}/bpm/bpl.json')

        if not res.ok:
            print(f"""FAILED\nSomething went wrong while fetching bpm from bpl, more information below:
\tError:\t\tHTTP {res.status_code} {res.reason}
\tLibrary:\t{BPL_URL}
\tResponse:\t{res.content.decode()}""")

            prompt("Try again?", stop_install)
        else:
            print("OK")
            break

    if install_packages:
        meta = res.json()
        print_task(f"Installing bpm-{meta['version']} ({meta['name']})")
        res = requests.get(f'{BPL_URL}/bpm/{meta["bin"]}')

        while install_packages:
            if not res.ok:
                print(f"""FAILED\nSomething went wrong while downloading bpm binaries, more information below:
\tError:\t\tHTTP {res.status_code} {res.reason}
\tLibrary:\t{BPL_URL}
\tResponse:\t{res.content.decode()}
\tRequested Bin:\t{meta['bin']}
\tMetadata:\t{meta}""")

                prompt("Try again?", stop_install)
            else:
                break

    if install_packages:
        with open(virtsh.get_path('exec', 'bpm'), 'wb') as f:
            f.write(res.content)

        print("OK")

        print_header("INSTALL PACKAGES")

        virtsh.run_line("bpm install -y core")

    else:
        print("[!] bpm could not be installed, no packages installed.")

    print_header("SETUP BADBANDSSH")

    key = RSAKey.generate(bits=2048)
    key.write_private_key_file(virtsh.get_path('cfg', 'badbandssh_rsa_key'))
    print("Stored BadBandSSH private key")

    print_header("CREATE LAUNCHER")
    if not os.path.exists("bin"):
        os.mkdir("bin")

    binpath = os.path.abspath(BDSH_SRC)

    if sys.platform.startswith("win"):
        with open(os.path.join("bin", "bdsh.bat"), "w") as f:
            f.write(f'@echo off\n{sys.executable} {binpath} %*')
        print("Created WINDOWS launcher")

    else:
        with open(os.path.join("bin", "bdsh"), "w") as f:
            f.write(f'#!/bin/bash\n{sys.executable} {binpath} "$@"')
        os.chmod(os.path.join("bin", "bdsh"), 0o755)
        if install_type is not InstallType.SYSTEM:
            print("Created UNIX launcher")
        else:
            print("Created launcher")

    if install_type is not InstallType.SYSTEM:
        print(
            f"[!] Please add the following path to your PATH after installation completes:\n\t{os.path.abspath('bin')}")
        getpass("Press ENTER to continue...")

    print_header("CLEANING UP")

    print("Done!\n")

    if install_type is not InstallType.SYSTEM:
        print(f"""After adding the bdsh binaries to PATH, you can run bdsh with:
    bdsh

Or, run the binary directly by running this file:
    {os.path.join(os.path.abspath('bin'), "bdsh.bat" if sys.platform.startswith("win") else "bdsh")}""")


if __name__ == "__main__":
    main()
