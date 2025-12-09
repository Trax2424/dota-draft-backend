import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Placeholder DB URL for now – we’ll override this on Railway later
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/dota_draft"

    class Config:
        env_file = ".env"

settings = Settings()
