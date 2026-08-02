import argparse
import re
from dataclasses import dataclass, field, fields
from typing import Callable, Literal, cast, TYPE_CHECKING
from urllib.parse import urlparse

import requests

from bdsh import __version__, OSPaths
from bdsh.command import Command
from bdsh.install.util import install_python_package
from bdsh.util.version import VersionSelector

if TYPE_CHECKING:
    from bdsh.session import Session

BPL_REPO = 'badtechnologies/bpl/main'
BPM_APP_DIR = OSPaths.APPLICATIONS.joinpath("bpm")  # for package installations
BPM_STORE_DIR = OSPaths.CONFIGS.joinpath("bpm")  # for a store of all packages

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


from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class StoreMetadata:
    name: str
    author: str
    binaries: list[Path]
    symlinks: list[Path]

    @classmethod
    def load(cls, file: Path) -> "StoreMetadata":
        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)

        return cls(
            name=data.get("name", "Unnamed package"),
            author=data.get("author", "Unknown author"),
            binaries=[Path(x) for x in data.get("binaries", [])],
            symlinks=[Path(x) for x in data.get("symlinks", [])],
        )

    def dump(self, file: Path) -> None:
        data = {
            "name": self.name,
            "author": self.author,
            "binaries": [str(x) for x in self.binaries],
            "symlinks": [str(x) for x in self.symlinks],
        }

        with file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


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

        if not self.packages:
            self.session.io.println("No packages to install!")
            return

        if not args.yes:
            while (s := self.session.io.input(
                    f"Install {len(self.packages)} package(s): {' '.join([p.id for p in self.packages])}? [Y/n] " or 'n'
            ).lower()) not in {'y', 'n'}:
                break
            # noinspection PyUnboundLocalVariable
            if s == 'n':
                return

        for package in self.packages:
            binaries = []
            symlinks = []

            # check compat. with bdsh/bados version
            if not VersionSelector(package.shellVersion).matches(__version__):
                self.session.io.println(
                    f"Package {package.id}-{package.version} ({package.name}) is not compatible with this version of BadOS!")
                continue

            self.session.io.println(f"Installing {package.id}-{package.version} ({package.name})")

            # create app folder and download binaries to it
            bin_folder = BPM_APP_DIR.joinpath(package.id, package.version)
            bin_folder.mkdir(parents=True, exist_ok=True)

            for bin_name, bin_repo_name in package.binaries.items():
                res = requests.get(get_bpl_uri(package.internal_repo, package.id, bin_repo_name))

                if res.status_code != 200:
                    self.session.io.println(
                        f"\tHTTP {res.status_code}; could not access binary '{bin_name}' for package '{package.id}'")
                    continue

                binary = bin_folder.joinpath(bin_name)
                binaries.append(binary)
                with open(binary, 'wb') as f:
                    f.write(res.content)

                symlink = OSPaths.EXECUTABLES.joinpath(bin_name)

                if symlink.exists():
                    replace = self.session.io.input(
                        f"Error while linking: {bin_name} already exists! Replace it? [Y/n] "
                    ).lower() or "y"

                    if replace != "y":
                        self.session.io.println("Skipped linking for this binary")
                        continue

                    symlink.unlink()

                symlink.symlink_to(binary)
                self.session.io.println(f"Linked {symlink} -> {binary}")
                symlinks.append(symlink)

            # store metadata
            store = BPM_STORE_DIR.joinpath(f"{package.id}@{package.version}.bpmstore")
            store.parent.mkdir(parents=True, exist_ok=True)
            StoreMetadata(name=package.name, author=package.author, binaries=binaries, symlinks=symlinks).dump(store)

            # install py deps
            if package.pythonDependencies:
                self.session.io.println(f"Installing Python dependencies for {package.id}")
                for dep, ver in package.pythonDependencies.items():
                    self.session.io.print(f"Install {dep}, {ver}... ")
                    install_python_package(f"{dep}{VersionSelector(ver).to_pip()}", printfn=self.session.io.println)

            # run setup script
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
            while (s := self.session.io.input(
                    f"Remove {len(args.packages)} package(s): {' '.join(args.packages)}? [Y/n] " or 'n'
            ).lower()) not in {'y', 'n'}:
                break
            # noinspection PyUnboundLocalVariable
            if s == 'n':
                return

        for package in args.packages:
            self.session.io.println(f"Deleting {package}...")

            store: dict[str, Path] = {}
            for file in BPM_STORE_DIR.glob("*.bpmstore"):
                if not file.name.startswith(package): return

                _id, version = file.name.removesuffix(".bpmstore").rsplit("@", 1)
                store[version] = file
            versions = list(store.keys())

            version = versions[0]
            if len(store) > 1:
                i = int(self.session.io.input("More than one version found! Please select a version to remove.\n\t"
                                              + "\n\t".join(f"{i}: {version}" for i, version in enumerate(store, 1))
                                              + "\n\t> "))
                version = versions[i - 1]

            meta = StoreMetadata.load(store[version])
            for binary in meta.binaries:
                if binary.exists():
                    binary.unlink()
                    self.session.io.println(f"\tDeleted binary: {str(binary)}")

            for symlink in meta.symlinks:
                symlink.unlink()
                self.session.io.println(f"\tUnlinked executable: {str(symlink.name)}")

            store[version].unlink()
            self.session.io.println(f"\tCompleted package deletion")

    def help(self) -> str:
        return parser.format_help()
