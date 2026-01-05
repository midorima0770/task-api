from fastapi import Depends,status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.auth_config import oauth2_scheme
from src.api.auth.auth_exceptions import EmailVerifiedException
from src.api.auth.auth_func import get_user_from_token
from src.api.project.project_crud import project_crud
from src.api.project.project_exceptions import ProjectNotFoundException
from src.api.task.task_crud import task_crud
from src.api.task.task_exceptions import TaskAlreadyExistsException, TasksNotFoundException, TaskNotFoundException, \
    TaskAccessForbiddenException, DeadlineExceededException, InvalidStatusTransitionException, \
    InvalidStatusTransitionInProgressException
from src.api.task.task_models import TaskStatusEnum
from src.api.task.task_schema import CreateTaskSchema
from src.api.users.users_exceptions import UserNotFoundException, ForbiddenException
from src.api.users.users_models import RoleEnum
from src.database import get_async_db

async def get_all_tasks_func(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    user_orm = await get_user_from_token(token, db)
    if not user_orm:
        raise UserNotFoundException()

    result = await task_crud.get_all_tasks(db=db,user=user_orm)
    if not result:
        raise TasksNotFoundException()

    return result

async def get_one_task_func(
    id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    user_orm = await get_user_from_token(token, db)
    if not user_orm:
        raise UserNotFoundException()

    task_orm = await task_crud.get_task_by_id(db=db,id=id)
    if not task_orm:
        raise TaskNotFoundException(id)

    if task_orm.assignee_id != user_orm.id:
        raise TaskAccessForbiddenException()

    return task_orm

async def create_task_func(
    new_task: CreateTaskSchema,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    user_orm = await get_user_from_token(token, db)
    if not user_orm:
        raise UserNotFoundException()

    new_task.assignee_id = user_orm.id

    flag_project = await project_crud.check_project_is_already_by_id(db=db,id=new_task.project_id)
    if not flag_project:
        raise ProjectNotFoundException(new_task.project_id)

    flag_task = await task_crud.check_task_is_already(db=db,new_task=new_task)
    if flag_task:
        raise TaskAlreadyExistsException(title=new_task.title,assignee_id=new_task.assignee_id)

    await task_crud.create_task(db=db,new_task=new_task)

    return {"status": status.HTTP_201_CREATED}

async def delete_task_func(
    id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    user_orm = await get_user_from_token(token, db)
    if not user_orm:
        raise UserNotFoundException()

    task_orm = await task_crud.get_task_by_id(db=db,id=id)
    if not task_orm:
        raise TaskNotFoundException(id)

    if user_orm.role != RoleEnum.user:
        res = await task_crud.delete_task(db=db,id=id)
        if res:
            return {"status": status.HTTP_200_OK}
        else:
            return {"status": status.HTTP_400_BAD_REQUEST}
    else:
        if task_orm.assignee_id == user_orm.id:
            res = await task_crud.delete_task(db=db, id=id)
            if res:
                return {"status": status.HTTP_200_OK}
            else:
                return {"status": status.HTTP_400_BAD_REQUEST}
        else:
            raise TaskAccessForbiddenException()

async def change_status_func(
    id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    user_orm = await get_user_from_token(token, db)
    if not user_orm:
        raise UserNotFoundException()

    task_orm = await task_crud.get_task_by_id(db=db, id=id)
    if not task_orm:
        raise TaskNotFoundException(id)

    if task_orm.assignee_id != user_orm.id:
        raise TaskAccessForbiddenException()

    res = await task_crud.change_status_without_new_status(db=db,id=id)

    return res

async def status_in_progress_func(
    id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    user_orm = await get_user_from_token(token, db)
    if not user_orm:
        raise UserNotFoundException()

    task_orm = await task_crud.get_task_by_id(db=db, id=id)
    if not task_orm:
        raise TaskNotFoundException(id)

    if task_orm.assignee_id != user_orm.id:
        raise TaskAccessForbiddenException()

    if task_orm.status == TaskStatusEnum.DONE:
        raise InvalidStatusTransitionInProgressException()

    res = await task_crud.change_status(db=db,new_status=TaskStatusEnum.IN_PROGRESS,id=id)
    if res is None:
        raise TaskNotFoundException(id)

    if not res:
        raise DeadlineExceededException()

    return {"status":status.HTTP_200_OK}

async def status_done_func(
    id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    user_orm = await get_user_from_token(token, db)
    if not user_orm:
        raise UserNotFoundException()


    task_orm = await task_crud.get_task_by_id(db=db, id=id)
    if not task_orm:
        raise TaskNotFoundException(id)

    if task_orm.assignee_id != user_orm.id:
        raise TaskAccessForbiddenException()

    if task_orm.status == TaskStatusEnum.TODO:
        raise InvalidStatusTransitionException()

    res = await task_crud.change_status(db=db,new_status=TaskStatusEnum.DONE,id=id)
    if res is None:
        raise TaskNotFoundException(id)

    if not res:
        raise DeadlineExceededException()

    return {"status":status.HTTP_200_OK}