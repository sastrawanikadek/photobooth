import json

from server.utils.supports.encoder import JSONEncoder


def json_serialize(value: object) -> str | None:
    """
    Serialize a value to a JSON string.

    Parameters
    ----------
    value : object
        The value to serialize.

    Returns
    -------
    str
        The serialized value.
    """
    if value is None or isinstance(value, str):
        return value

    return json.dumps(value, cls=JSONEncoder)


def json_deserialize(value: object) -> object:
    """
    Deserialize a JSON string to a value.

    Parameters
    ----------
    value : str
        The value to deserialize.

    Returns
    -------
    object
        The deserialized value.
    """
    if value is None or (
        not isinstance(value, str)
        and not isinstance(value, bytes)
        and not isinstance(value, bytearray)
    ):
        return value

    try:
        return json.loads(value)
    except Exception:
        return value
