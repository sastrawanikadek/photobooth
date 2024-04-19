from typing import TYPE_CHECKING
from uuid import UUID, uuid5

from server.constants import APP_UUID_NAMESPACE

if TYPE_CHECKING:
    from .models import SettingOption, ValueType

_TYPE_MAPPING = {
    "integer": int,
    "boolean": bool,
    "string": str,
    "float": float,
    "list": list,
}


def generate_setting_uuid(source: str, key: str) -> UUID:
    """
    Generate a UUID for a setting.

    Parameters
    ----------
    source : str
        The source of the setting, it can be "system" or component slug.
    key : str
        The key of the setting.

    Returns
    -------
    UUID
        The UUID of the setting.
    """
    return uuid5(APP_UUID_NAMESPACE, f"{source}/{key}")


def is_valid_value(type: "ValueType", value: object, required: bool = False) -> bool:
    """
    Check if a value is valid for a setting type.

    Parameters
    ----------
    type : ValueType
        The setting type.
    value : object
        The value to check.
    required : bool
        Whether the value is required, if True, None is not a valid value, by default False.

    Returns
    -------
    bool
        Whether the value is valid for the setting type.
    """
    if required:
        return isinstance(value, _TYPE_MAPPING[type])

    return value is None or isinstance(value, _TYPE_MAPPING[type])


def is_value_match_option(
    options: list[str] | list["SettingOption"], value: object
) -> bool:
    """
    Check if a value matches any of the options.

    Parameters
    ----------
    options : list[str] | list[SettingOption]
        The options to check.
    value : object
        The value to check.

    Returns
    -------
    bool
        Whether the value matches any of the options.
    """
    return any(
        [
            option == value if isinstance(option, str) else option.value == value
            for option in options
        ]
    )
