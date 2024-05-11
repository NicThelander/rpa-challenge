from loguru import logger

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Shared config, can pull these in from an env file for production environment but just hard coding for the sake of it being a project"""
    LOGGING_TITLE: str = "rpa_project"

try:
    settings = Settings()

    # example of handling when for if we were pulling it through env vars
    for s in settings.model_fields:
        if s == None:
            raise Exception(f"Missing environment variable {s}")
except Exception as e:
    logger.exception(e)
    exit(1)