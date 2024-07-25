from getpass import getpass
import bdsh
import json
import os
import sys
import subprocess

PYREQS_URL = "https://raw.githubusercontent.com/badtechnologies/bdsh/main/requirements.txt"
GIT_URL = "https://github.com/badtechnologies/bdsh"
BDSH_SRC_URL = "https://raw.githubusercontent.com/badtechnologies/bdsh/main/bdsh.py"
BPL_URL = "https://raw.githubusercontent.com/badtechnologies/bpl/main/lib"

PYREQS = "requirements.txt"
BDSH_SRC = "bdsh.py"

BDSH_DIRS = ['cfg', 'prf', 'exec']
BDSH_ROOT = "bdsh"


def install_package(package_name: str):
    package_name = package_name.strip()
    try:
        print(f"\nInstalling '{package_name}'")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package_name])
        print(f"Python package '{package_name}' installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Python package '{package_name}': {e}")


def prompt(prompt: str, on_cancel: callable, **default: str):
    while (s := input((prompt + " [y/n] ") or default).lower()) not in {'y', 'n'}:
        pass
    if s == 'n':
        on_cancel()


def print_header(header: str):
    print('\n'+(f" {header} ").center(50, '='))


if __name__ == "__main__":
    prompt("This will replace your current bdsh configs, proceed?", lambda: exit(0))

    print_header("SETUP ENV")

    if 'VIRTUAL_ENV' not in os.environ:
        prompt("This will install bdsh-required Python packages to your current env. Continue?", lambda: exit(0))

    print("Upgrading pip...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    except subprocess.CalledProcessError as e:
        print(f"Failed to upgrade pip: {e}")

    install_package("requests")
    import requests

    if os.path.exists(PYREQS):
        print("Package list already download, skipping")
    else:
        print(f"\nDownloading package list...")

        res = requests.get(PYREQS_URL)

        if not res.ok:
            print(f"Failed to fetch package list, please download it manually from the bdsh repo: {GIT_URL}")
            exit(0)

        with open(PYREQS, 'wb') as f:
            f.write(res.content)
        print(f"Downloaded package list.")

    print("\nInstalling packages...")
    with open(PYREQS, 'r') as f:
        for line in f.readlines():
            install_package(line)

    print("\nCleaning up...")
    os.remove(PYREQS)

    # IMPORT STATEMENTS (AFTER INSTALLING PIP PACKAGES)
    from paramiko import RSAKey

    print_header("DOWNLOAD BDSH")

    if os.path.exists(BDSH_SRC):
        print("bdsh source already downloaded, skipping")
    else:
        res = requests.get(BDSH_SRC_URL)

        if not res.ok:
            print(f"Failed to fetch bdsh source, please download it manually from the bdsh repo: {GIT_URL}")
            exit(0)

        with open(BDSH_SRC, 'wb') as f:
            f.write(res.content)

        print("Downloaded bdsh source successfully")

    print_header("INIT BDSH")

    try:
        if not os.path.exists(BDSH_ROOT):
            os.mkdir(BDSH_ROOT)

        for dir in BDSH_DIRS:
            path = os.path.join(BDSH_ROOT, dir)
            if not os.path.exists(path):
                os.mkdir(path)
    except Exception as e:
        print(f"Error initializing bdsh directory structure: {e}")
        exit(-1)

    print(f"Populated bdsh root ({BDSH_ROOT}/) successfully")

    print("Starting virtual bdsh session")
    virtsh = bdsh.Shell(sys.stdout, sys.stdin)
    print(bdsh.Shell(None, None).header)

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

        def exitloop():
            global username
            username = None

        prompt("Create another?", exitloop)

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
    while install_packages:
        res = requests.get(f'{BPL_URL}/bpm/bpl.json')

        if not res.ok:
            print(f"""Something went wrong while fetching bpm from bpl, more information below:
\tError:\t\tHTTP {res.status_code} {res.reason}
\tLibrary:\t{BPL_URL}
\tResponse:\t{res.content.decode()}""")

            prompt("Try again?", lambda: globals().update(install_packages=False))
        else:
            break

    if install_packages:
        meta = res.json()
        print(f"Installing bpm-{meta['version']} ({meta['name']})")
        res = requests.get(f'{BPL_URL}/bpm/{meta["bin"]}')

        while install_packages:
            if not res.ok:
                print(f"""Something went wrong while downloading bpm binaries, more information below:
\tError:\t\tHTTP {res.status_code} {res.reason}
\tLibrary:\t{BPL_URL}
\tResponse:\t{res.content.decode()}
\tRequested Bin:\t{meta['bin']}
\tMetadata:\t{meta}""")

                prompt("Try again?", lambda: globals().update(install_packages=False))
            else:
                break

    if install_packages:
        with open(virtsh.get_path('exec', 'bpm'), 'wb') as f:
            f.write(res.content)

        print(f"Installation complete: bpm is installed")

        print_header("INSTALL PACKAGES")

        virtsh.run_line("bpm install -y core")

    else:
        print("[!] bpm could not be installed, no packages installed.")

    print_header("SETUP BADBANDSSH")

    key = RSAKey.generate(bits=2048)
    key.write_private_key_file(virtsh.get_path('cfg', 'badbandssh_rsa_key'))
    print("Stored BadBandSSH private key")

    print_header("CREATE LAUNCHER SCRIPTS")
    if not os.path.exists("bin"):
        os.mkdir("bin")

    binpath = os.path.abspath(BDSH_SRC)

    if sys.platform.startswith("win"):
        with open(os.path.join("bin", "bdsh.bat"), "w") as f:
            f.write(f'@echo off\n{sys.executable} {binpath} %*')
        print("Created WINDOWS launcher script")

    else:
        with open(os.path.join("bin", "bdsh"), "w") as f:
            f.write(f'#!/bin/bash\n{sys.executable} {binpath} "$@"')
        os.chmod(os.path.join("bin", "bdsh"), 0o755)
        print("Created UNIX launcher script")

    print_header("CLEANING UP")

    print("Done!")
