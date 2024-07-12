import requests
import argparse
import json
from typing import List
import os


def parse_cli_args():
    parser = argparse.ArgumentParser(description='BadOS Package Manager')

    parser.add_argument(
        'action',
        type=str,
        choices=['install', 'remove', 'fetchcore'],
        help='action to perform'
    )

    parser.add_argument(
        'packages',
        nargs='+',
        type=str,
        help='packages to manage'
    )

    return parser.parse_args()


class PackageException(Exception):
    def __init__(self, package: str, message: str):
        super().__init__(f"{package}: {message}")


class Package:
    def __init__(self, name, id, version, author, bin=None, homepage=None, requires=None):
        self.name = name
        self.id = id
        self.version = version
        self.author = author
        self.bin_uri = f'https://raw.githubusercontent.com/badtechnologies/bdsh/main/bpl/{id}/{bin}' if bin is not None else None
        self.homepage = homepage
        self.requires = requires if requires is not None else []

    def __repr__(self):
        return (f"BPL_Package(name={self.name}, version={self.version}, author={self.author}, "
                f"bin={self.bin_uri}, homepage={self.homepage}, requires={self.requires})")

    @staticmethod
    def load_json(package, data):
        return Package(
            name=data['name'],
            id=package,
            version=data['version'],
            author=data['author'],
            bin=data.get('bin'),
            homepage=data.get('homepage'),
            requires=data.get('requires', [])
        )

    @staticmethod
    def fetch(package: str):
        res = requests.get(
            f'https://raw.githubusercontent.com/badtechnologies/bdsh/main/bpl/{package}/bpl.json')

        if res.status_code == 200:
            return Package.load_json(package, json.loads(res.content))
        elif res.status_code == 404:
            raise PackageException(
                package, "does not exist or could not be found")
        else:
            raise PackageException(
                package, f"something went wrong. HTTP {res.status_code} while fetching package data")


packages: List[Package] = []


def process_package(_pkg):
    try:
        package = Package.fetch(_pkg)
        print(f"\t{_pkg}: found '{package.name}' v{package.version}")
        packages.append(package)
        return package.requires if package.requires else []
    except PackageException as e:
        print('\t'+str(e))
        return []


def main():
    args = parse_cli_args()

    if args.action == 'install':
        print("Discovering packages and dependencies...")

        deps = []
        for package in args.packages:
            deps.extend(process_package(package))

        while deps:
            new_deps = []
            for package in deps:
                new_deps.extend(process_package(package))
            deps = new_deps

        print()

        while (s := input((f"Install {len(packages)} package(s): {' '.join([p.id for p in packages])}? [Y/n] ") or 'n').lower()) not in {'y', 'n'}:
            pass
        if s == 'n':
            exit()

        for package in packages:
            print(
                f"Installing {package.id}-{package.version} ({package.name})")

            if package.bin_uri is None:
                continue

            res = requests.get(package.bin_uri)

            if res.status_code != 200:
                print(
                    f"\tHTTP {res.status_code}; could not access package binaries")
                continue

            with open(f'bdsh/exec/{package.id}', 'wb') as f:
                f.write(res.content)

    elif args.action == 'remove':
        while (s := input((f"Remove {len(args.packages)} package(s): {' '.join(args.packages)}? [Y/n] ") or 'n').lower()) not in {'y', 'n'}:
            pass
        if s == 'n':
            exit()

        for package in args.packages:
            print(f"Deleting {package}")
            path = f"bdsh/exec/{package}"

            if not os.path.exists(path):
                print("\tCould not find package, skipping")
                continue

            os.remove(path)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
