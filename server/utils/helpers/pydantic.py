from pydantic import ValidationError


def validation_error(
    field: str,
    message: str,
    title: str = "Validation Error",
    type: str = "value_error",
    input: object | None = None,
) -> ValidationError:
    """
    Create a validation error for a field.

    Parameters
    ----------
    field : str
        The field that the error occurred on.
    message : str
        The error message.
    title : str
        The title of the error, defaults to "Validation Error".
    type : str
        The type of error, defaults to "value_error".
    input : object | None
        The input that caused the error.

    Returns
    -------
    ValidationError
        The validation error.
    """
    return ValidationError.from_exception_data(
        title=title,
        line_errors=[
            {
                "loc": (field,),
                "type": type,
                "ctx": {
                    "error": message,
                },
                "input": input,
            }
        ],
    )
