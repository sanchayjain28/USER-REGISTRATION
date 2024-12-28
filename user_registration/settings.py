import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

settings = {
    "PORT": os.getenv("PORT"),
    "USER": os.getenv("DB_USER"),
    "PASSWORD": os.getenv("DB_PASSWORD"),
    "HOST": os.getenv("DB_HOST"),
    "DB_PORT": os.getenv("DB_PORT"),
    "DATABASE": os.getenv("DB_NAME"),
    'HASH_KEY': os.getenv("HASH_KEY"),
    "SECRET_KEY": os.getenv("SECRET_KEY"),
    "ALGORITHM": os.getenv("ALGORITHM"),
    "ACCESS_TOKEN_EXPIRE_MINUTES": os.getenv("ACCESS_TOKEN_EXPIRE_MIN"),
    "REFRESH_TOKEN_EXPIRE_MINUTES": os.getenv("REFRESH_TOKEN_EXPIRE_MIN")
}