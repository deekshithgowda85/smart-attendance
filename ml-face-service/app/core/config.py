import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Server
    ML_SERVICE_HOST: str = "0.0.0.0"
    ML_SERVICE_PORT: int = 8001
    
    # Face Recognition
    MIN_FACE_AREA_RATIO: float = 0.05
    NUM_JITTERS: int = 5
    CONFIDENCE_THRESHOLD: float = 0.50
    UNCERTAIN_THRESHOLD: float = 0.60
    
    # Storage
    EMBEDDINGS_STORAGE_PATH: str = "./storage/embeddings"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Ensure storage directory exists
os.makedirs(settings.EMBEDDINGS_STORAGE_PATH, exist_ok=True)
