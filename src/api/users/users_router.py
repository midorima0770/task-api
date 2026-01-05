from fastapi import APIRouter, Depends,status,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.auth_config import oauth2_scheme
from src.api.users.users_exceptions import UserNotFoundException
from src.database import get_async_db

from src.api.users.users_func import get_users_db
from src.api.users.users_func import get_one_user_by_id_db

users = APIRouter(tags=["users"],prefix="/users")

@users.get("/get/all")
async def get_users(
    users=Depends(get_users_db)  # FastAPI сам передаст token и db
):
    return users
