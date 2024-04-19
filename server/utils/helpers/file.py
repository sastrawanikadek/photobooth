import time
import uuid
from typing import IO


def get_file_size(io: IO) -> int:
    """
    Get the size of a file.

    Parameters
    ----------
    io : IO
        The file object.

    Returns
    -------
    int
        The size of the file in bytes.
    """
    io.seek(0, 2)
    size = io.tell()
    io.seek(0)

    return size


def generate_filename() -> str:
    """Generate a unique filename based on the current timestamp and identifier."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    identifier = uuid.uuid4()

    return f"{timestamp}_{identifier}"
