# task-api 

This is an API project written using the Fastapi + sqlalchemy framework.
I chose postgresql as the database.

Therefore, at the beginning, after pull, create a .env file in which you pass the following values:
  
  -DATABASE_URL = "postgresql+asyncpg://user_db_name:user_db_password@localhost:5432/db_name" <----------- Change to your values ​​before launching 
  -SECRET_KEY = your_secret_key
  -ALGORITHM = "HS256"
  -ACCESS_TOKEN_EXPIRE_MINUTES = 30
  -REFRESH_TOKEN_EXPIRE_DAYS = 7
  -ADMIN_NAME = your_admin_name
  -ADMIN_PAS = yoour_admin_pas
