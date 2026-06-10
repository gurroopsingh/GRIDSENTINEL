"""GRIDSENTINEL-X Ω — Configuration"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "GRIDSENTINEL-X Ω"
    debug: bool = True

    # Database
    database_url: str = "sqlite+aiosqlite:///./gridsentinel.db"

    # Redis
    redis_url: str = ""

    # AI
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # Simulation
    simulation_tick_seconds: float = 3.0
    grid_cities: list[str] = ["Mumbai", "Delhi", "Bengaluru", "Chennai"]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
