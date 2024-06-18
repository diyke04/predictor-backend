from pydantic_settings import BaseSettings
from enum import Enum

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./predictor.db"
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    ORIGINS:list =['http://localhost:5173']

    class Config:
        env_file = ".env"

settings = Settings()



class RewardType(Enum):
    POST_PREDICTION = 1
    CORRECT_SCORE = 5
    CORRECT_RESULT = 2

