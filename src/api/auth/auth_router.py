from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.auth_config import oauth2_scheme
from src.api.auth.auth_exceptions import InvalidCredentialsLoginException, InvalidRefreshTokenException, \
    InvalidTokenException, UserAlreadyExistsException, EmailNotVerifiedException, EmailVerifiedException, \
    UserOtpNotFoundException, IncorrectUserOtpException, ExpiredUserOtpException
from src.api.auth.auth_func import auth_func_register, login, refresh_token_func, get_me_func, get_otp_func, \
    send_otp_func, delete_me_func
from src.api.users.users_exceptions import UserNotFoundException
from src.database import get_async_db

from src.api.auth.auth_schema import RegisterSchema, Token, SendOTP, GetOTP
from src.exceptions import logger

auth = APIRouter(prefix="/auth",tags=["auth"])



# Роутер на регистрацию
@auth.post("/register")
async def auth_register(
    register_schema: RegisterSchema,
    db: AsyncSession = Depends(get_async_db)
):
    try:
        return await auth_func_register(name=register_schema.name,email=register_schema.email,password=register_schema.password,db=db)
    except UserAlreadyExistsException:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"User with name{register_schema.name} is already")
    except Exception as e:
        logger.exception(e)

# Роутер на вход
@auth.post("/login", response_model=Token)
async def auth_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        return await login(form_data=form_data,db=db)
    except InvalidCredentialsLoginException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=f"User with name={form_data.username} is not already or password is not correct")
    except EmailNotVerifiedException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Email not verified")
    except Exception as e:
        logger.exception(e)

# Роутер на обновление токена
@auth.post("/refresh", response_model=Token)
async def auth_refresh_token(
    refresh_token: str
):
    try:
        return await refresh_token_func(refresh_token)
    except InvalidRefreshTokenException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid refresh token")
    except Exception as e:
        logger.exception(e)

@auth.get("/me")
async def get_me(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        return await get_me_func(token=token,db=db)
    except InvalidTokenException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")
    except Exception as e:
        logger.exception(e)

@auth.delete("/me")
async def delete_me(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        return await delete_me_func(token=token,db=db)
    except InvalidTokenException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")
    except Exception as e:
        logger.exception(e)

@auth.post("/get_otp")
async def get_otp(
    get_otp: GetOTP,
    db: AsyncSession = Depends(get_async_db)
):
    try:
        return await get_otp_func(get_otp.email,db)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"User with email:{get_otp.email} not found")
    except EmailVerifiedException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Email:{get_otp.email} verified")
    except Exception as e:
        logger.exception(e)

@auth.post("/send_otp")
async def send_otp(
    send_otp: SendOTP,
    db: AsyncSession = Depends(get_async_db)
):
    try:
        return await send_otp_func(send_otp.email,send_otp.otp,db)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with email:{send_otp.email} not found")
    except EmailVerifiedException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Email:{send_otp.email} verified")
    except UserOtpNotFoundException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=UserOtpNotFoundException().message)
    except IncorrectUserOtpException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=IncorrectUserOtpException().message)
    except ExpiredUserOtpException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=ExpiredUserOtpException().message)
    except Exception as e:
        logger.exception(e)