from fastapi import status

from src.exceptions import AppException

class UserAlreadyExistsException(AppException):
    def __init__(self,name):
        super().__init__(
            message=f"User with name:{name} is already",
            status_code=status.HTTP_409_CONFLICT
        )

class EmailAlreadyExistsException(AppException):
    def __init__(self,email):
        super().__init__(
            message=f"User with email:{email} is already",
            status_code=status.HTTP_409_CONFLICT
        )

class InvalidCredentialsLoginException(AppException):
    def __init__(self,name):
        super().__init__(
            message=f"User with name={name} is not already or password is not correct",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class InvalidRefreshTokenException(AppException):
    def __init__(self):
        super().__init__(
            message="Invalid refresh token",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class InvalidTokenException(AppException):
    def __init__(self):
        super().__init__(
            message="Invalid token",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class EmailNotVerifiedException(AppException):
    def __init__(self,email):
        super().__init__(
            message=f"Email:{email} not verified",
            status_code=status.HTTP_403_FORBIDDEN
        )

class EmailVerifiedException(AppException):
    def __init__(self,email):
        super().__init__(
            message=f"Email:{email} verified",
            status_code=status.HTTP_403_FORBIDDEN
        )

class UserOtpNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            message=f"User_otp not found",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class IncorrectUserOtpException(AppException):
    def __init__(self):
        super().__init__(
            message=f"User_otp is incorrect",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class ExpiredUserOtpException(AppException):
    def __init__(self):
        super().__init__(
            message=f"Expired OTP",
            status_code=status.HTTP_401_UNAUTHORIZED
        )