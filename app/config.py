from pydantic_settings import BaseSettings  # <- pydantic v2 style

class Settings(BaseSettings):
    # Default DB for local = SQLite file
    DATABASE_URL: str = "sqlite:///./dev.db"
    database_url: str = "sqlite:///./dev.db"

    class Config:
        env_file = ".env"
        extra = "ignore"  # ignore any extra env vars so nothing explodes

settings = Settings()
