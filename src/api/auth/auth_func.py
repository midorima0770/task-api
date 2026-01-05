from datetime import datetime,timedelta

from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.auth_config import oauth2_scheme
from src.api.auth.auth_schema import Token
from src.api.auth.otp import generate_otp, send_otp
from src.api.auth.token_func import create_access_token, create_refresh_token, verify_token
from src.api.users.users_exceptions import UserNotFoundException
from src.api.users.users_models import UserOrm
from src.database import get_async_db
from src.api.auth.auth_crud import auth_crud

from src.api.auth.auth_exceptions import UserAlreadyExistsException, InvalidCredentialsLoginException, \
    InvalidRefreshTokenException, InvalidTokenException, EmailNotVerifiedException, EmailAlreadyExistsException, \
    EmailVerifiedException, UserOtpNotFoundException, IncorrectUserOtpException, ExpiredUserOtpException

from src.api.auth.security import hash_password,verify_password

from zoneinfo import ZoneInfo

# Функция регистрации
async def auth_func_register(
    name: str,
    email: str,
    password: str,
    db: AsyncSession = Depends(get_async_db)
):
    auth_orm = await auth_crud.check_user_is_already(db,name)
    if auth_orm is not None:
        raise UserAlreadyExistsException(name)
    auth_orm = await auth_crud.check_user_is_already_email(db=db,email=email)
    if auth_orm is not None:
        raise EmailAlreadyExistsException(email)
    password = hash_password(password)
    await auth_crud.register_user(db=db,name=name,email=email,password=password)
    return {"status": status.HTTP_201_CREATED}

# Функция логина
async def login(form_data: OAuth2PasswordRequestForm = Depends(),db: AsyncSession = Depends(get_async_db)):
    # Проверяем пользователя по имени
    user_orm = await auth_crud.check_user_is_already(name=form_data.username,db=db)

    if not user_orm or not verify_password(plain_password=form_data.password,hashed_password=user_orm.password):
        raise InvalidCredentialsLoginException(form_data.username)
    if not user_orm.is_verified:
        raise EmailNotVerifiedException(user_orm.email)

    # Создаем токены
    data = {"sub": str(user_orm.id)}
    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)

    return Token(access_token=access_token, refresh_token=refresh_token)

# Функция для обновления токена
async def refresh_token_func(refresh_token: str):
    payload = verify_token(refresh_token)
    if not payload:
        raise InvalidRefreshTokenException()

    new_access = create_access_token({"sub": payload["sub"], "username": payload["username"]})
    new_refresh = create_refresh_token({"sub": payload["sub"], "username": payload["username"]})

    return Token(access_token=new_access, refresh_token=new_refresh)

# -----------------------------
# Чистая логика, можно вызывать напрямую
# -----------------------------
async def get_user_from_token(token: str, db: AsyncSession):
    """
    Получить пользователя из токена.
    Выбрасывает InvalidTokenException если токен неверный.
    """
    payload = verify_token(token)
    if not payload:
        raise InvalidTokenException()

    user_id = int(payload.get("sub"))
    user_orm = await auth_crud.get_user_crud(db=db, id=user_id)
    return user_orm


async def get_user_role_from_token(token: str, db: AsyncSession):
    """
    Получить роль пользователя из токена.
    """
    user_orm = await get_user_from_token(token, db)
    return user_orm.role


# -----------------------------
# Функции для использования с Depends в роутере
# -----------------------------
async def auth_get_user_func(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    return await get_user_from_token(token, db)


async def auth_check_role_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    return await get_user_role_from_token(token, db)

async def get_me_func(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    user_orm = await get_user_from_token(token, db)

    return {
        "id": user_orm.id,
        "name":user_orm.name,
        "projects": user_orm.projects
    }

async def delete_me_func(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    user_orm = await get_user_from_token(token, db)

    await db.delete(user_orm)
    await db.commit()

    return {"status":status.HTTP_200_OK}

async def get_otp_func(
    email: str,
    db: AsyncSession = Depends(get_async_db)
):
    user_orm = await auth_crud.get_user_by_email(db=db,email=email)
    if not user_orm:
        raise UserNotFoundException()

    if user_orm.is_verified:
        raise EmailVerifiedException(email)

    otp = generate_otp()
    await send_otp(email,otp)
    created_at = datetime.now(ZoneInfo("Europe/Moscow"))
    expires_at = created_at + timedelta(seconds=120)

    user_otp = await auth_crud.get_user_otp(db=db,id=user_orm.id)
    if not user_otp:
        res = await auth_crud.create_user_otp(
            db=db,
            user_id = user_orm.id,
            hash_otp=hash_password(otp),
            created_at=created_at,
            expires_at=expires_at
        )
        return "You will receive an OTP code by email."

async def send_otp_func(
    email: str,
    otp: str,
    db: AsyncSession = Depends(get_async_db)
):
    user_orm = await auth_crud.get_user_by_email(db=db, email=email)
    if not user_orm:
        raise UserNotFoundException()

    if user_orm.is_verified:
        raise EmailVerifiedException(email)

    user_otp = await auth_crud.get_user_otp(db=db,id=user_orm.id)
    if not user_otp:
        return UserOtpNotFoundException()

    if verify_password(otp,user_otp.hash_otp) and user_otp.expires_at > datetime.now(ZoneInfo("Europe/Moscow")):
        user_orm.is_verified = True
        await db.delete(user_otp)
        await db.commit()
        return {"status":status.HTTP_200_OK}
    elif not verify_password(otp,user_otp.hash_otp):
        raise IncorrectUserOtpException()
    elif user_otp.expires_at < datetime.now(ZoneInfo("Europe/Moscow")):
        raise ExpiredUserOtpException()
