from dotenv import load_dotenv
import os

from pydantic.v1 import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: str = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: str = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")

    ADMIN_NAME: str = os.getenv("ADMIN_NAME")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL")
    ADMIN_PAS: str = os.getenv("ADMIN_PAS")

    class Config:
        env_file = ".env"

settings = Settings()