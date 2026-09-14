from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    telegram_bot_token:str

    ollama_host:str = "http://localhost:11434"
    ollama_model:str

    second_brain_path:Path
    database_path:Path = Path("data/reasearch.db")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()