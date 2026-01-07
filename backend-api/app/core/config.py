import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import List


load_dotenv()

APP_NAME = "Smart Attendance API"

# CORS origins
ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


class Settings(BaseSettings):
    MONGO_URI: str = os.getenv("MONGO_URI")
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    
class Config:
    env_file = ".env"

settings = Settings()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL")
