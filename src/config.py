from loguru import logger
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Shared config, can pull these in from an env file for production
    environment but just hard coding for the sake of it being a project"""
    ENV: str = "local"
    PROJECT_TITLE: str = "rpa_project"
    LOGGING_FILE: str = "../logs/rpa_project.log"
    STARTUP_FAIL_LOG_FILE_PATH: str = "../logs/startup_failure.log"
    LOGGING_LEVEL: str = "INFO"
    SCREENSHOT_FOLDER_PATH: str = "../screenshots"
    DEFAULT_SLEEP: float = 0.05
    DEFAULT_TIMEOUT: int = 20
    OUTPUT_PATH: str = "../output"


try:
    settings = Settings()

    # example of handling when for if we were pulling it through env vars
    for s in settings.model_fields:
        if s == None:
            raise Exception(f"Missing environment variable {s}")
except Exception as e:
    logger.exception(e)
    exit(1)
