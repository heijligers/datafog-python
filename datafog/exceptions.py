# exceptions.py


class DataFogException(Exception):
    """Base exception for DataFog SDK"""

    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class BadRequestError(DataFogException):
    """Exception raised for 400 Bad Request errors"""

    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class UnprocessableEntityError(DataFogException):
    """Exception raised for 422 Unprocessable Entity errors"""

    def __init__(self, message: str):
        super().__init__(message, status_code=422)


def raise_for_status_code(status_code: int, error_message: str):
    """Raise the appropriate exception based on the status code"""
    if status_code == 400:
        raise BadRequestError(error_message)
    elif status_code == 422:
        raise UnprocessableEntityError(error_message)
