from getpass import getpass
import bdsh
import json
import os
from paramiko import RSAKey


def prompt(prompt: str, on_cancel: callable, **default: str):
    while (s := input((prompt + " [y/n] ") or default).lower()) not in {'y', 'n'}:
        pass
    if s == 'n':
        on_cancel()


def print_header(header: str):
    print('\n'+(f" {header} ").center(50, '='))


if __name__ == "__main__":
    prompt("This will replace your current bdsh configs, proceed?", lambda: exit(0))

    print_header("INIT BDSH")
    print(bdsh.get_header().decode())

    dirs = ['core', 'cfg', 'prf', 'exec']

    try:
        if not os.path.exists('bdsh'):
            os.mkdir('bdsh')

        for dir in dirs:
            path = os.path.join('bdsh', dir)
            if not os.path.exists(path):
                os.mkdir(path)
    except Exception as e:
        print(f"Error initializing bdsh directory structure: {e}")
        exit(-1)

    print("Populated /bdsh successfully")

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

    with open('bdsh/cfg/users.json', 'w') as f:
        json.dump(users, f)

    for username in users.keys():
        path = os.path.join('bdsh/prf', username)
        if not os.path.exists(path):
            os.mkdir(path)

    print(f"Created {len(users)} user(s)")

    print_header("SETUP BADBANDSSH")

    key = RSAKey.generate(bits=2048)
    key.write_private_key_file('bdsh/cfg/badbandssh_rsa_key')
    print("Stored BadBandSSH private key")

    print_header("CLEANING UP")

    print("Done!")
