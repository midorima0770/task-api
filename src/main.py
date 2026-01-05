from fastapi import FastAPI

from src.api import main_router
from src.database import AsyncSessionLocal, drop_all_tables, create_all_tables, engine
from src.exceptions import AppException, app_exception_handler, logger
from src.config import settings
from src.api.auth.auth_crud import auth_crud

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def create_all():
    async with AsyncSessionLocal() as db:

        #await drop_all_tables(engine)

        await create_all_tables(engine)

        flag = await auth_crud.check_user_is_already(db=db,name=settings.ADMIN_NAME)
        if flag:
            logger.warning("Admin acc is already created")
        else:
            await auth_crud.create_admin(db=db, name=settings.ADMIN_NAME,email=settings.ADMIN_EMAIL,password=settings.ADMIN_PAS)
            logger.warning("Admin acc was creatd")

# Регистрируем обработчик всех кастомных ошибок
app.add_exception_handler(AppException, app_exception_handler)

# Регистрируем главный роутер , подробнее о роутерах в src.api.__init__.py
app.include_router(main_router)