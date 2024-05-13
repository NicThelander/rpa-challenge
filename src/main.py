# built ins
import asyncio
from datetime import datetime
import os

# installed libs
from loguru import logger
from selenium.webdriver.chrome.options import Options
from robocorp.tasks import task

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
        # timestamp for output file and folder
        output_sub_folder = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path = os.path.join(settings.OUTPUT_PATH, output_sub_folder)
        os.makedirs(path, exist_ok=True)

        logger.info("Instantiating NewsBrowser")
        news_browser = NewsBrowser(
            logger=logger
        )
        logger.info("Instantiating NewsBrowser")

        news_browser.open_browser(url="https://gothamist.com/search")

        output_data = news_browser.search_articles(
            output_sub_dir=output_sub_folder,
            query=search_term,
            months=months
        )
        news_browser.close_browsers()

        path = f"{settings.OUTPUT_PATH}/{output_sub_folder}/output.xlsx"
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
    project(settings.SEARCH_QUERY, settings.MONTHS)
    
# if __name__ == '__main__':
#     project("dog")
