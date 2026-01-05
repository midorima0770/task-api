from fastapi import APIRouter, Depends,status,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.auth_config import oauth2_scheme
from src.api.auth.auth_exceptions import EmailVerifiedException, EmailNotVerifiedException
from src.api.project.project_exceptions import ProjectsNotFoundException, ProjectNotFoundException, \
    ProjectAccessForbiddenException, ProjectAlreadyExistsException
from src.api.project.project_func import get_all_projects_func, create_project_func, delete_project_func, \
    change_title_project_func, change_des_func, get_one_project_func
from src.api.project.project_schema import CreateProjectSchema, ChangeTitleSchema, ChangeDescriptionSchema
from src.api.users.users_exceptions import UserNotFoundException, ForbiddenException
from src.database import get_async_db
from src.exceptions import logger

project = APIRouter(prefix="/project",tags=["project"])

# Нет ограничений на права
@project.get("/all")
async def get_all_projects(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        return await get_all_projects_func(token=token,db=db)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"User not found")
    except ProjectsNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Projects not found")
    except Exception as e:
        logger.exception(e)

@project.get("/one")
async def get_one_project(
    id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        return await get_one_project_func(id=id,token=token,db=db)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")
    except ProjectNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Project with id = {id} not found")
    except ProjectAccessForbiddenException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"You do not have permission to access this project.")
    except Exception as e:
        logger.exception(e)

# Есть ограничения на права
@project.post("/create",status_code=status.HTTP_201_CREATED)
async def create_project(
    new_project:CreateProjectSchema,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        return await create_project_func(new_project=new_project,token=token,db=db)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")
    except ProjectAlreadyExistsException:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Project with title = {new_project.title} , and owner_id = {new_project.owner_id} is already")
    except ForbiddenException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"You do not have permission to perform this action")
    except Exception as e:
        logger.exception(e)

# Есть ограничения на права
@project.delete("/delete")
async def delete_project(
    id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        return await delete_project_func(id=id,token=token,db=db)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")
    except ProjectNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Project with id = {id} not found")
    except ProjectAccessForbiddenException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"You do not have permission to access this project.")
    except Exception as e:
        logger.exception(e)

# Есть ограничения
@project.patch("/change/title")
async def change_title(
    new_title_schema: ChangeTitleSchema,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        return await change_title_project_func(new_title_schema=new_title_schema,token=token,db=db)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")
    except ProjectNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Project not found")
    except ProjectAccessForbiddenException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"You do not have permission to access this project.")
    except Exception as e:
        logger.exception(e)

@project.patch("/change/des")
async def change_des(
    new_des_schema: ChangeDescriptionSchema,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        return await change_des_func(new_des_schema=new_des_schema,token=token,db=db)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")
    except ProjectNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Project not found")
    except ProjectAccessForbiddenException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"You do not have permission to access this project.")
    except Exception as e:
        logger.exception(e)