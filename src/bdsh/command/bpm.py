import argparse
import json
import os
from typing import List

import requests

from bdsh.command import Command

BPL_REPO = 'badtechnologies/bpl/main'

parser = argparse.ArgumentParser(description='BadOS Package Manager')
parser.add_argument('action', type=str, choices=['install', 'remove'], help='action to perform')
parser.add_argument('packages', nargs='+', type=str, help='packages to manage')
parser.add_argument('-y', '--yes', action='store_true',
                    help='assume "yes" as the answer to all prompts and run non-interactively')
parser.add_argument('-r', '--repo', default=BPL_REPO,
                    help='set repo to download from, in the format "owner/repo/branch", must be on GitHub')


class PackageException(Exception):
    def __init__(self, package: str, message: str):
        super().__init__(f"{package}: {message}")


class Package:
    def __init__(self, name, id, version, author, bin=None, homepage=None, requires=None, repo=BPL_REPO):
        self.name = name
        self.id = id
        self.version = version
        self.author = author
        self.bin_uri = f'https://raw.githubusercontent.com/{repo}/lib/{id}/{bin}' if bin is not None else None
        self.homepage = homepage
        self.requires = requires if requires is not None else []
        self.repo = repo

    def __repr__(self):
        return f"BPL_Package(name={self.name}, version={self.version}, author={self.author}, bin={self.bin_uri}, homepage={self.homepage}, requires={self.requires})"

    @staticmethod
    def load_json(package, data, repo):
        return Package(
            name=data['name'],
            id=package,
            version=data['version'],
            author=data['author'],
            bin=data.get('bin'),
            homepage=data.get('homepage'),
            requires=data.get('requires', []),
            repo=repo
        )

    @staticmethod
    def fetch(package: str, repo):
        res = requests.get(f'https://raw.githubusercontent.com/{repo}/lib/{package}/bpl.json')

        if res.status_code == 200:
            return Package.load_json(package, json.loads(res.content), repo)
        elif res.status_code == 404:
            raise PackageException(package, "does not exist or could not be found")
        else:
            raise PackageException(package, f"something went wrong. HTTP {res.status_code} while fetching package data")


packages: List[Package] = []


def process_package(_pkg, repo: str):
    try:
        package = Package.fetch(_pkg, repo)
        print(f"\t{_pkg}: found '{package.name}' v{package.version}")
        packages.append(package)
        return package.requires if package.requires else []
    except PackageException as e:
        print('\t' + str(e))
        return []


class BadOSPackageManagerCommand(Command):
    def execute(self, args: List[str]):
        try:
            args = parser.parse_args(args[1:])
        except SystemExit:
            return

        if args.action == 'install':
            print("Discovering packages and dependencies...")

            deps = []
            for package in args.packages:
                deps.extend(process_package(package, args.repo))

            while deps:
                new_deps = []
                for package in deps:
                    new_deps.extend(process_package(package, args.repo))
                deps = new_deps

            print()

            if not args.yes:
                while (s := input(
                        f"Install {len(packages)} package(s): {' '.join([p.id for p in packages])}? [Y/n] " or 'n').lower()) not in {
                    'y', 'n'}:
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
            if not args.yes:
                while (s := input(
                        f"Remove {len(args.packages)} package(s): {' '.join(args.packages)}? [Y/n] " or 'n').lower()) not in {
                    'y', 'n'}:
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

    def help(self) -> str:
        return "re-run this program with the `--help` arg for the manual page"
