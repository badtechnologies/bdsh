"""
Provides useful types aliases around bdsh.

Author: Logan Dhillon <dev@logandhillon.com>
"""


from typing import Mapping, Sequence, TypeAlias


Serializable: TypeAlias = (
    Mapping[str, "Serializable"]
    | Sequence["Serializable"]
    | str
    | int
    | float
    | bool
    | None
)

SerializableDict: TypeAlias = Mapping[str, "Serializable"]
