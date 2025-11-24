from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from typing import Union
from .formatter import ErrorResponse


async def validation_exception_handler(
    request: Request,
    exc: Union[RequestValidationError, Exception]
) -> ErrorResponse:
    """Handle validation errors and return BaseResponse format"""
    if isinstance(exc, RequestValidationError):
        errors = exc.errors()
        error_details = []
        for error in errors:
            field = error.get('loc', [])[-1] if error.get('loc') else 'field'
            msg = error.get('msg', 'Validation error')
            error = {
                "field": str(field),
                "message": msg
            }
            error_details.append(error)
        return ErrorResponse(
            message="Validation error",
            error=error_details,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    return ErrorResponse(
        message="Validation error",
        error=str(exc),
        status_code=status.HTTP_400_BAD_REQUEST
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
) -> ErrorResponse:
    """Handle general exceptions and return BaseResponse format"""

    error_details = []
    # If the exception has an 'args' attribute and it's a tuple, use it; else use str(exc)
    if hasattr(exc, 'args') and exc.args:
        for idx, arg in enumerate(exc.args):
            error_details.append({"error": str(arg)})
    else:
        error_details.append({"error": str(exc)})


    return ErrorResponse(
        message="An unexpected error occurred",
        success=False,
        error=error_details,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
