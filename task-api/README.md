# task-api 

This is an API project written using the Fastapi + sqlalchemy framework.
I chose postgresql as the database.

1).Therefore, at the beginning, after pull, create a .env file in which you pass the following values:
  
  -DATABASE_URL = "postgresql+asyncpg://user_db_name:user_db_password@localhost:5432/db_name" <----------- Change to your values ​​before launching 
  -SECRET_KEY = your_secret_key
  -ALGORITHM = "HS256"
  -ACCESS_TOKEN_EXPIRE_MINUTES = 30
  -REFRESH_TOKEN_EXPIRE_DAYS = 7
  -ADMIN_NAME = your_admin_name
  -ADMIN_PAS = yoour_admin_pas

2).The next step is to create venv and activate it.

3).Download all dependencies via pip using the command:
  pip install -r requirements/base.txt

4).After this, you can run the project via uvicorn:
  uvicorn src.main:app --reload <----------- for localhost run
  uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload <----------- ASGI-server Uvicorn , if the port is in use, change it
