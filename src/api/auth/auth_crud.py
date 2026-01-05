from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.auth.security import hash_password
from src.api.db.base_crud import BaseCRUD
from src.api.users.users_models import UserOrm, RoleEnum, UserOTP


# CRUD auth
class AuthBaseCrud(BaseCRUD):

    model=UserOrm

    # Для создания админа
    async def create_admin(self,db: AsyncSession,name,email,password):
        user_orm = UserOrm(
            name=name,
            email=email,
            password=hash_password(password),
            role=RoleEnum.admin,
            is_verified=True
        )
        db.add(user_orm)
        await db.commit()

    # Для проверки дубликата имени
    async def check_user_is_already(self,db: AsyncSession,name: str):
        result = await db.execute(select(self.model).where(
            self.model.name == name
        ))
        return result.scalars().one_or_none()

    async def check_user_is_already_email(self, db: AsyncSession, email: str):
        result = await db.execute(select(self.model).where(
            self.model.email == email
        ))
        return result.scalars().one_or_none()

    # Регистрация
    async def register_user(self,db: AsyncSession,name: str,email: str,password: str):
        user_orm = UserOrm(
            name=name,
            email=email,
            password=password,
            role=RoleEnum.user,
            is_verified=False
        )
        db.add(user_orm)
        await db.commit()

    async def get_user_crud(self, db: AsyncSession, id: int):
        result = await db.execute(
            select(UserOrm)
            .options(selectinload(UserOrm.projects))  # предзагрузка проектов
            .where(UserOrm.id == id)
        )
        return result.scalars().one_or_none()

    async def get_user_by_email(self,db: AsyncSession,email: str):
        result = await db.execute(
            select(UserOrm)
            .options(selectinload(UserOrm.projects))  # предзагрузка проектов
            .where(UserOrm.email == email)
        )
        return result.scalars().one_or_none()

    async def get_all_users(self,db: AsyncSession):
        result = await db.execute(select(UserOrm).options(selectinload(UserOrm.projects)))
        users_orm = result.scalars().all()

        if users_orm:
            return users_orm
        else:
            return None

    async def create_user_otp(
        self,
        db: AsyncSession,
        user_id,
        hash_otp,
        created_at,
        expires_at
    ):
        user_otp = UserOTP(
            user_id=user_id,
            hash_otp=hash_otp,
            created_at=created_at,
            expires_at=expires_at
        )
        db.add(user_otp)
        await db.commit()

    async def get_user_otp(
        self,
        id: int,
        db: AsyncSession,
    ):
        result = await db.execute(select(UserOTP).where(
            UserOTP.user_id==id
        ))
        user_otp = result.scalars().one_or_none()
        return user_otp

auth_crud = AuthBaseCrud(UserOrm)