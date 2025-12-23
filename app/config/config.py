from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):    
    PROJECT_NAME: str = "Software License Classification API"
    VERSION: str = "1.0.0"
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    GROQ_TEMPERATURE: float = 0.3
    GROQ_MAX_TOKENS: int = 200
    
    VALID_CATEGORIES: List[str] = [
        "Productivity",
        "Design",
        "Communication",
        "Development",
        "Finance",
        "Marketing"
    ]
    MAX_EXPLANATION_LENGTH: int = 150
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()