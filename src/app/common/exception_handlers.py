from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Union

async def validation_exception_handler(
    request: Request, 
    exc: Union[RequestValidationError, Exception]
) -> JSONResponse:
    """Handle validation errors and return BaseResponse format"""
    if isinstance(exc, RequestValidationError):
        errors = exc.errors()
        error_messages = []
        
        for error in errors:
            # Extract the error message
            msg = error.get('msg', 'Validation error')
            
            # For value_error type, clean up the message
            if error.get('type') == 'value_error':
                msg = msg.replace('Value error, ', '')
            else:
                # For other errors, include the field name
                field = error.get('loc', [])[-1] if error.get('loc') else 'field'
                msg = f"{field}: {msg}"
            
            error_messages.append(msg)
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": None,
                "message": error_messages[0] if len(error_messages) == 1 else '; '.join(error_messages)
            }
        )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "data": None,
            "message": "Validation error"
        }
    )

async def general_exception_handler(
    request: Request, 
    exc: Exception
) -> JSONResponse:
    """Handle general exceptions and return BaseResponse format"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "data": None,
            "message": str(exc) if str(exc) else "An unexpected error occurred"
        }
    )