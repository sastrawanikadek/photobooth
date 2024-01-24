import importlib
import inspect
from pathlib import Path
from types import ModuleType
from typing import TypeVar, cast

_CT = TypeVar("_CT", bound=type)


def import_module_by_path(path: Path) -> ModuleType | None:
    """
    Import a module by path.

    Parameters
    ----------
    path : Path
        The path to the module.

    Returns
    -------
    ModuleType | None
        The module if it exists, None otherwise.
    """

    try:
        module_name = ".".join(str(path).split("/"))
        return importlib.import_module(module_name)
    except ImportError:
        return None


def get_module_class(
    module: ModuleType, name: str | None = None, cls_type: _CT | None = None
) -> _CT | None:
    """
    Get a class from a module.

    Parameters
    ----------
    module : ModuleType
        The module to get the class from.
    name : str | None
        The name of the class to get.
    cls_type : type
        The type of the class to get.

    Returns
    -------
    type
        The class if it exists, None otherwise.
    """
    classes = [
        cls[1]
        for cls in inspect.getmembers(module, inspect.isclass)
        if (
            (name is None or cls[0] == name)
            and (
                cls_type is None
                or (cls[1] is not cls_type and issubclass(cls[1], cls_type))
            )
        )
        or cls[1].__module__ == module.__name__
    ]

    if len(classes) == 0:
        return None

    return cast(_CT, classes[0])


def get_calling_module() -> ModuleType | None:
    """
    Get the module of the calling function.

    Returns
    -------
    ModuleType | None
        The module of the calling function if it exists, None otherwise.
    """
    stack = inspect.stack()

    if stack is None or len(stack) < 3:
        return None

    frame = stack[2].frame
    module = inspect.getmodule(frame)

    return module
