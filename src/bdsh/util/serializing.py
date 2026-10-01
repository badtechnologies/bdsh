from typing import TypeAlias

JsonPrimitive: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]


def validate_json_value(value, path="value") -> None:
    if value is None or isinstance(value, (str, int, float, bool)):
        return

    if isinstance(value, list):
        for index, item in enumerate(value):
            validate_json_value(item, f"{path}[{index}]")
        return

    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise SerializationError(
                    f"{path} contains a non-string dictionary key of type {type(key).__name__}")
            validate_json_value(item, f"{path}[{key!r}]")
        return

    raise SerializationError(f"{path} contains unsupported type {type(value).__name__}; must be json-serializable")


class SerializationError(Exception):
    pass
