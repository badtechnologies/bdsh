import argparse
import json
import os
import re
from dataclasses import dataclass, field, fields
from typing import Callable, Literal, cast, TYPE_CHECKING
from urllib.parse import urlparse

import requests

import bdsh
from bdsh.command import Command
from bdsh.install.util import install_python_package, print_task
from bdsh.util.version import VersionSelector

if TYPE_CHECKING:
    from bdsh.session import Session

BPL_REPO = 'badtechnologies/bpl/main'

parser = argparse.ArgumentParser(description='BadOS Package Manager', color=False, add_help=False)
parser.add_argument('action', type=str, choices=['install', 'remove'], help='action to perform')
parser.add_argument('packages', nargs='+', type=str, help='packages to manage')
parser.add_argument('-y', '--yes', action='store_true',
                    help='assume "yes" as the answer to all prompts and run non-interactively')
parser.add_argument('-r', '--repo', default=BPL_REPO,
                    help='set repo to download from, in the format "owner/repo/branch", must be on GitHub')


class BpmArgs(argparse.Namespace):
    action: Literal["install", "remove"]
    packages: list[str]
    yes: bool
    repo: str


def get_bpl_uri(repo: str, id: str, file: str):
    return f'https://raw.githubusercontent.com/{repo}/lib/{id}/{file}'


VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
ID_PATTERN = re.compile(r"^[a-z0-9-]+$")
VERSION_CONSTRAINT_PATTERN = re.compile(
    r"^(\*|\^?\d+\.\d+\.\d+|~\d+\.\d+\.\\d+|>=?\d+\.\d+\.\d+|<=?\d+\.\d+\.\d+)$"
)


class DependencyMap(dict[str, str]):
    def __init__(self, dependencies: dict[str, str] | None = None):
        super().__init__(dependencies or {})

        for name, version in self.items():
            if not ID_PATTERN.match(name):
                raise ValueError(f"Invalid dependency name: {name}")

            if not VERSION_CONSTRAINT_PATTERN.match(version):
                raise ValueError(f"Invalid dependency version constraint: {version}")


@dataclass
class Package:
    internal_repo: str
    internal_package: str

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

    @staticmethod
    def load_json(package, data, repo):

        kwargs = {
            key.name: data[key.name]
            for key in fields(Package)
            if key.name in data
        }
        kwargs["internal_repo"] = repo
        kwargs["internal_package"] = package
        return Package(**kwargs)

    @staticmethod
    def fetch(package: str, repo):
        res = requests.get(f'https://raw.githubusercontent.com/{repo}/lib/{package}/bpl.json')

        if res.status_code == 200:
            return Package.load_json(package, json.loads(res.content), repo)
        elif res.status_code == 404:
            raise PackageException(package, "does not exist or could not be found")
        else:
            raise PackageException(package, f"something went wrong. HTTP {res.status_code} while fetching package data")


class PackageException(Exception):
    def __init__(self, package: str, message: str):
        super().__init__(f"{package}: {message}")


class BadOSPackageManagerCommand(Command):
    def __init__(self, session: Session):
        super().__init__(session)
        self.packages: list[Package] = []
        self.handlers: dict[str, Callable[[BpmArgs], None]] = {
            "install": self.__install,
            "remove": self.__remove,
        }

    def execute(self, args: list[str]):
        self.packages.clear()

        try:
            args = cast(BpmArgs, parser.parse_args(args[1:]))
        except SystemExit:
            return

        self.handlers[args.action](args)

    def __discover_package_dependencies(self, _pkg, repo: str) -> list[str]:
        try:
            pkg = Package.fetch(_pkg, repo)
            self.session.io.println(f"\t{_pkg}: found '{pkg.name}' v{pkg.version}")
            self.packages.append(pkg)
            return pkg.dependencies.keys() if pkg.dependencies else []
        except PackageException as e:
            self.session.io.println('\t' + str(e))
            return []

    def __install(self, args: BpmArgs):
        self.session.io.println("Discovering packages and dependencies...")

        deps = []
        for package in args.packages:
            deps.extend(self.__discover_package_dependencies(package, args.repo))

        while deps:
            new_deps = []
            for package in deps:
                new_deps.extend(self.__discover_package_dependencies(package, args.repo))
            deps = new_deps

        self.session.io.println()

        if not args.yes:
            while (s := input(
                    f"Install {len(self.packages)} package(s): {' '.join([p.id for p in self.packages])}? [Y/n] " or 'n').lower()) not in {
                'y', 'n'}:
                pass
            if s == 'n':
                raise ValueError("user exited program with code 0")

        for package in self.packages:
            if not VersionSelector(package.shellVersion).matches(bdsh.__version__):
                self.session.io.println(
                    f"Package {package.id}-{package.version} ({package.name}) is not compatible with this version of BadOS!")
                continue

            self.session.io.println(f"Installing {package.id}-{package.version} ({package.name})")

            os.makedirs(bdsh.get_shell_path("exec", package.id), exist_ok=True)

            for bin_name, bin_repo_name in package.binaries.items():
                res = requests.get(get_bpl_uri(package.internal_repo, package.id, bin_repo_name))

                if res.status_code != 200:
                    self.session.io.println(
                        f"\tHTTP {res.status_code}; could not access binary '{bin_name}' for package '{package.id}'")
                    continue

                with open(bdsh.get_shell_path("exec", package.id, bin_name), 'wb') as f:
                    f.write(res.content)

            if package.pythonDependencies:
                self.session.io.print(f"Installing Python dependencies for {package.id}")
                for dep, ver in package.pythonDependencies.items():
                    print_task(f"Install {dep}, {ver}")
                    install_python_package(f"{dep}{VersionSelector(ver).to_pip()}")

            for i, script in enumerate(package.setupScripts):
                res = requests.get(get_bpl_uri(package.internal_repo, package.id, script))

                if res.status_code != 200:
                    self.session.io.println(
                        f"\tHTTP {res.status_code}; could not access setup script '{script}' for package '{package.id}'")
                    continue

                self.session.io.println(f"Executing setup script ({i}/{len(package.setupScripts)})...")
                exec(res.content.decode())
            self.session.io.println("Done!")

    def __remove(self, args: BpmArgs):
        if not args.yes:
            while (s := input(
                    f"Remove {len(args.packages)} package(s): {' '.join(args.packages)}? [Y/n] " or 'n').lower()) not in {
                'y', 'n'}:
                pass
            if s == 'n':
                raise ValueError("user exited program with code 0")

        for package in args.packages:
            self.session.io.println(f"Deleting {package}")
            path = bdsh.get_shell_path("exec", package)

            if not os.path.exists(path):
                self.session.io.println("\tCould not find package, skipping")
                continue

            os.remove(path)

    def help(self) -> str:
        return parser.format_help()
