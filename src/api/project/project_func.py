from fastapi import Depends,status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.auth_config import oauth2_scheme
from src.api.auth.auth_crud import auth_crud
from src.api.auth.auth_exceptions import EmailVerifiedException
from src.api.auth.auth_func import auth_get_user_func, get_user_role_from_token, get_user_from_token
from src.api.auth.token_func import verify_token
from src.api.project.project_exceptions import ProjectsNotFoundException, ProjectAlreadyExistsException, \
    ProjectNotFoundException, ProjectAccessForbiddenException
from src.api.project.project_schema import CreateProjectSchema, ChangeTitleSchema, ChangeDescriptionSchema
from src.api.users.users_exceptions import UserNotFoundException, ForbiddenException
from src.api.users.users_models import RoleEnum
from src.database import get_async_db

from src.api.project.project_crud import project_crud

async def get_all_projects_func(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    user_orm = await auth_get_user_func(token=token, db=db)

    if user_orm is None:
        raise UserNotFoundException()

    projects = await project_crud.get_all_projects(db=db,user_id=user_orm.id,user_role=user_orm.role)

    if projects is None or projects == []:
        raise ProjectsNotFoundException()

    return projects

async def get_one_project_func(
    id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    user_orm = await get_user_from_token(token, db)
    if not user_orm:
        raise UserNotFoundException()

    project_orm = await project_crud.get_project_by_id(db=db,id=id)
    if not project_orm:
        raise ProjectNotFoundException(id)

    if user_orm.role != RoleEnum.user:
        return project_orm
    else:
        if project_orm.owner_id == user_orm.id:
            return project_orm
        else:
            raise ProjectAccessForbiddenException()

async def create_project_func(
    new_project:CreateProjectSchema,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    user_orm = await get_user_from_token(token, db)
    if not user_orm:
        raise UserNotFoundException()

    if user_orm.id == new_project.owner_id:

        flag = await project_crud.check_project_is_already(db=db,title=new_project.title,owner_id=new_project.owner_id)
        if flag:
            raise ProjectAlreadyExistsException(title=new_project.title,owner_id=new_project.owner_id)

        await project_crud.create_project(db=db,new_project=new_project)

        return {"status":status.HTTP_201_CREATED}

    else:
        raise ForbiddenException()

async def delete_project_func(
    id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    user_orm = await get_user_from_token(token, db)
    if not user_orm:
        raise UserNotFoundException()
    project = await project_crud.get_project_by_id(db=db,id=id)
    if project is None:
        raise ProjectNotFoundException(id)
    if user_orm.role != RoleEnum.user:
        res = await project_crud.delete_project(db=db,id=id)
        if res:
            return {"status": status.HTTP_200_OK}
        else:
            return {"status": status.HTTP_400_BAD_REQUEST}
    else:
        if project.owner_id == user_orm.id:
            res = await project_crud.delete_project(db=db,id=id)
            if res:
                return {"status":status.HTTP_200_OK}
            else:
                return {"status": status.HTTP_400_BAD_REQUEST}
        else:
            raise ProjectAccessForbiddenException()

async def change_title_project_func(
    new_title_schema: ChangeTitleSchema,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    user_orm = await get_user_from_token(token, db)
    if not user_orm:
        raise UserNotFoundException()
    project = await project_crud.get_project_by_id(db=db, id=new_title_schema.id)
    if project is None:
        raise ProjectNotFoundException(new_title_schema.id)

    if project.owner_id == user_orm.id:
        result = await project_crud.change_title(db=db,id=project.id,new_title=new_title_schema.new_title)
        return result
    else:
        raise ProjectAccessForbiddenException()

async def change_des_func(
    new_des_schema: ChangeDescriptionSchema,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    user_orm = await get_user_from_token(token, db)
    if not user_orm:
        raise UserNotFoundException()
    project = await project_crud.get_project_by_id(db=db, id=new_des_schema.id)
    if project is None:
        raise ProjectNotFoundException(new_des_schema.id)

    if project.owner_id == user_orm.id:
        result = await project_crud.change_description(db=db,id=project.id,new_description=new_des_schema.new_description)
        return result
    else:
        raise ProjectAccessForbiddenException()