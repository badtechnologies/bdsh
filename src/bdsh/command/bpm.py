import argparse
import json
import os
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from urllib.parse import urlparse

import requests

from bdsh import get_shell_path
from bdsh.command import Command

if TYPE_CHECKING:
    from bdsh.shell import Shell

BPL_REPO = 'badtechnologies/bpl/main'

parser = argparse.ArgumentParser(description='BadOS Package Manager')
parser.add_argument('action', type=str, choices=['install', 'remove'], help='action to perform')
parser.add_argument('packages', nargs='+', type=str, help='packages to manage')
parser.add_argument('-y', '--yes', action='store_true',
                    help='assume "yes" as the answer to all prompts and run non-interactively')
parser.add_argument('-r', '--repo', default=BPL_REPO,
                    help='set repo to download from, in the format "owner/repo/branch", must be on GitHub')

VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
ID_PATTERN = re.compile(r"^[a-z0-9-]+$")
VERSION_CONSTRAINT_PATTERN = re.compile(
    r"^(\*|\^?\d+\.\d+\.\d+|~\d+\.\d+\.\\d+|>=?\d+\.\d+\.\d+|<=?\d+\.\d+\.\d+)$"
)


@dataclass
class DependencyMap:
    dependencies: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        for name, version in self.dependencies.items():
            if not ID_PATTERN.match(name):
                raise ValueError(f"Invalid dependency name: {name}")

            if not VERSION_CONSTRAINT_PATTERN.match(version):
                raise ValueError(f"Invalid dependency version constraint: {version}")


@dataclass
class PackageManifest:
    name: str
    id: str
    version: str
    author: str
    shellVersion: str

    binaries: dict[str, str] = field(default_factory=dict)
    setupScripts: list[str] = field(default_factory=list)
    homepage: str | None = None
    license: str | None = None
    dependencies: DependencyMap | None = None
    pythonDependencies: DependencyMap | None = None

    def __post_init__(self):
        if not ID_PATTERN.match(self.id):
            raise ValueError(f"Invalid id: {self.id}")

        if not VERSION_PATTERN.match(self.version):
            raise ValueError(f"Invalid version: {self.version}")

        if not VERSION_CONSTRAINT_PATTERN.match(self.shellVersion):
            raise ValueError(f"Invalid shellVersion: {self.shellVersion}")

        if self.homepage:
            parsed = urlparse(self.homepage)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"Invalid homepage URI: {self.homepage}")


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


class BadOSPackageManagerCommand(Command):
    def __init__(self, shell: Shell):
        super().__init__(shell)
        self.packages: list[Package] = []

    def execute(self, args: list[str]):
        self.packages.clear()

        try:
            args = parser.parse_args(args[1:])
        except SystemExit:
            return

        if args.action == 'install':
            self.__install(args)
        elif args.action == 'remove':
            self.__remove(args)


    def __process_package(self, _pkg, repo: str):
        try:
            pkg = Package.fetch(_pkg, repo)
            print(f"\t{_pkg}: found '{pkg.name}' v{pkg.version}")
            self.packages.append(pkg)
            return pkg.requires if pkg.requires else []
        except PackageException as e:
            print('\t' + str(e))
            return []

    def __install(self, args):
        print("Discovering packages and dependencies...")

        deps = []
        for package in args.packages:
            deps.extend(self.__process_package(package, args.repo))

        while deps:
            new_deps = []
            for package in deps:
                new_deps.extend(self.__process_package(package, args.repo))
            deps = new_deps

        print()

        if not args.yes:
            while (s := input(
                    f"Install {len(self.packages)} package(s): {' '.join([p.id for p in self.packages])}? [Y/n] " or 'n').lower()) not in {
                'y', 'n'}:
                pass
            if s == 'n':
                exit()

        for package in self.packages:
            print(
                f"Installing {package.id}-{package.version} ({package.name})")

            if package.bin_uri is None:
                continue

            res = requests.get(package.bin_uri)

            if res.status_code != 200:
                print(
                    f"\tHTTP {res.status_code}; could not access package binaries")
                continue

            with open(get_shell_path("exec", package.id), 'wb') as f:
                f.write(res.content)

    def __remove(self, args):
        if not args.yes:
            while (s := input(
                    f"Remove {len(args.packages)} package(s): {' '.join(args.packages)}? [Y/n] " or 'n').lower()) not in {
                'y', 'n'}:
                pass
            if s == 'n':
                exit()

        for package in args.packages:
            print(f"Deleting {package}")
            path = get_shell_path("exec", package)

            if not os.path.exists(path):
                print("\tCould not find package, skipping")
                continue

            os.remove(path)

    def help(self) -> str:
        return "re-run this program with the `--help` arg for the manual page"
