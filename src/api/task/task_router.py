from fastapi import APIRouter, status, Depends, WebSocket, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.auth_config import oauth2_scheme
from src.api.auth.auth_exceptions import EmailNotVerifiedException
from src.api.project.project_exceptions import ProjectNotFoundException
from src.api.task.task_exceptions import TaskNotFoundException, TasksNotFoundException, TaskAccessForbiddenException, \
    TaskAlreadyExistsException, InvalidStatusTransitionInProgressException, DeadlineExceededException, \
    InvalidStatusTransitionException
from src.api.task.task_func import create_task_func, get_all_tasks_func, delete_task_func, get_one_task_func, \
    status_in_progress_func, status_done_func, change_status_func
from src.api.task.task_schema import CreateTaskSchema
from src.api.task.ws.ws_func import ws_task_func
from src.api.users.users_exceptions import UserNotFoundException
from src.database import get_async_db, AsyncSessionLocal
from src.exceptions import logger

task = APIRouter(tags=["task"],prefix="/task")

@task.websocket("/ws")
async def ws_task(websocket: WebSocket):
    await websocket.accept()

    token = websocket.query_params.get("token")

    async with AsyncSessionLocal() as db:
        await ws_task_func(websocket=websocket, token=token, db=db)

@task.get("/all")
async def get_all_tasks(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        return await get_all_tasks_func(token=token,db=db)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")
    except TasksNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Tasks not found")
    except Exception as e:
        logger.exception(e)

@task.get("/one")
async def get_one_task(
    id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        return await get_one_task_func(id=id,token=token,db=db)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")
    except TaskNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Task with id = {id} not found")
    except Exception as e:
        logger.exception(e)

@task.post("/create",status_code=status.HTTP_201_CREATED)
async def create_task(
    new_task: CreateTaskSchema,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        return await create_task_func(new_task=new_task,token=token,db=db)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")
    except ProjectNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Project with id = {new_task.project_id} not found")
    except TaskAlreadyExistsException:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Task with title = {new_task.title} , and owner_id = {new_task.assignee_id} is already")
    except Exception as e:
        logger.exception(e)

@task.delete("/delete")
async def delete_task(
    id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        return await delete_task_func(id=id,token=token,db=db)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")
    except TaskNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with id = {id} not found")
    except TaskAccessForbiddenException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"You do not have permission to access this task.")
    except Exception as e:
        logger.exception(e)

@task.patch("/status/change")
async def change_status(
    id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        return await change_status_func(id=id,token=token,db=db)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")
    except TaskNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with id = {id} not found")
    except TaskAccessForbiddenException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have permission to access this task.")
    except Exception as e:
        logger.exception(e)

@task.patch("/status/in_progress")
async def status_in_progress(
    id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        return await status_in_progress_func(id=id,token=token,db=db)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")
    except TaskNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with id = {id} not found")
    except TaskAccessForbiddenException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have permission to access this task.")
    except InvalidStatusTransitionInProgressException:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=
        f"You cannot change the status from done to in_progress"
        )
    except DeadlineExceededException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=
        f"The task's deadline has already passed, you cannot change the task's status."
        )
    except Exception as e:
        logger.exception(e)

@task.patch("/status/done")
async def status_done(
    id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        return await status_done_func(id=id,token=token,db=db)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")
    except TaskNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with id = {id} not found")
    except TaskAccessForbiddenException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have permission to access this task.")
    except InvalidStatusTransitionException:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=
        f"You cannot change the status from todo to done"
        )
    except DeadlineExceededException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=
        f"The task's deadline has already passed, you cannot change the task's status."
        )
    except Exception as e:
        logger.exception(e)