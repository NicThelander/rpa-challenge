# built ins
import asyncio
from datetime import datetime
import os

# installed libs
from robocorp.tasks import task
from robocorp import workitems
# from RPA.Robocorp.WorkItems import WorkItems

# project modules
from config import settings
from helpers.browsing import NewsBrowser
from helpers.util import output_excel_data
from logger import setup_logger


# went with a plain non async setup as unfamiliar with robocorp and how it
# plays with the async libraries
def project(search_term, months=1):
    try:
        logger = setup_logger()
        logger.info(f"Setting up {settings.PROJECT_TITLE}")
        logger.info(f"Environment set to {settings.ENV}")
        logger.info(f"Logging level set to {settings.LOGGING_LEVEL}")
        logger.info(f"Logging to {settings.LOGGING_FILE}")
        logger.info("Logger setup complete")
    except Exception as e:
        error_message = f"Failed to setup logger, reason: {e}"
        print(error_message)
        print(f"error logged to {settings.STARTUP_FAIL_LOG_FILE_PATH}")
        exit(1)

    try:
        logger.info("Instantiating NewsBrowser")
        news_browser = NewsBrowser(
            logger=logger
        )
        logger.info("Instantiating NewsBrowser")

        news_browser.open_browser(url="https://gothamist.com/search")

        output_data = news_browser.search_articles(
            query=search_term,
            months=months
        )
        news_browser.close_browsers()

        path = f"{settings.OUTPUT_PATH}/output.xlsx"
        output_excel_data(
            logger=logger,
            path=path,
            data=output_data
        )

    except Exception as e:
        logger.exception(f"Project failed to start, reason: {e}")
        raise

@task
def minimal_task():
    item = workitems.inputs.current
    search_query = item.payload.get("search_query")
    months = item.payload.get("months")
    project(search_query, months)
