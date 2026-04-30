from fastapi import HTTPException, status


class ErrorCode:
    SUCCESS = 0
    BAD_REQUEST = 40000
    UNAUTHORIZED = 40001
    FORBIDDEN = 40003
    NOT_FOUND = 40004
    BUSINESS_ERROR = 40009
    VALIDATION_ERROR = 40022
    SERVER_ERROR = 50000


def unauthorized(message: str = "unauthorized") -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={
        "code": ErrorCode.UNAUTHORIZED,
        "message": message,
        "data": None,
    })


def forbidden(message: str = "forbidden") -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={
        "code": ErrorCode.FORBIDDEN,
        "message": message,
        "data": None,
    })


def not_found(message: str = "not found") -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
        "code": ErrorCode.NOT_FOUND,
        "message": message,
        "data": None,
    })


def business_error(message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> HTTPException:
    return HTTPException(status_code=status_code, detail={
        "code": ErrorCode.BUSINESS_ERROR,
        "message": message,
        "data": None,
    })
