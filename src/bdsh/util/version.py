import re
from dataclasses import dataclass


@dataclass
class VersionSelector:
    operator: str
    version: tuple[int, int, int]

    def __init__(self, selector: str):
        self.original = selector.strip()

        match = re.match(
            r"^(?P<op>\^|~|>=|<=|>|<|=)?(?P<version>\d+\.\d+\.\d+|\*)$",
            self.original
        )

        if not match:
            raise ValueError(f"Invalid version selector: {selector}")

        self.operator = match.group("op") or "="

        version = match.group("version")
        self.version = None if version == "*" else self.parse_version(version)

    @staticmethod
    def parse_version(version: str) -> tuple[int, int, int]:
        parts = version.split(".", 2)
        return tuple(map(int, parts))

    def to_pip(self) -> str:
        if self.version is None:
            return ""

        version = ".".join(map(str, self.version))

        if self.operator == "=":
            return f"=={version}"

        if self.operator == "~":
            return f"~={version}"

        if self.operator == ">":
            return f">{version}"

        if self.operator == ">=":
            return f">={version}"

        if self.operator == "<":
            return f"<{version}"

        if self.operator == "<=":
            return f"<={version}"

        if self.operator == "^":
            major, minor, patch = self.version

            if major > 0:
                return f">={version},<{major + 1}.0.0"

            if minor > 0:
                return f">={version},<0.{minor + 1}.0"

            return f">={version},<0.0.{patch + 1}"

        raise ValueError(f"Unsupported operator: {self.operator}")

    def matches(self, version: str) -> bool:
        """
        Checks whether a semver version satisfies this selector.
        """

        if self.version is None:
            return True

        target = self.parse_version(version)

        if self.operator == "=":
            return target == self.version

        if self.operator == ">":
            return target > self.version

        if self.operator == ">=":
            return target >= self.version

        if self.operator == "<":
            return target < self.version

        if self.operator == "<=":
            return target <= self.version

        if self.operator == "~":
            # ~1.2.3 allows >=1.2.3 and <1.3.0
            return self.version <= target < (self.version[0], self.version[1] + 1, 0)

        if self.operator == "^":
            major, minor, patch = self.version

            if major > 0:
                upper = (major + 1, 0, 0)
            elif minor > 0:
                upper = (0, minor + 1, 0)
            else:
                upper = (0, 0, patch + 1)

            return target >= self.version and target < upper

        raise ValueError(f"Unsupported operator: {self.operator}")
