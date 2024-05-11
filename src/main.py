# built ins
import asyncio

# installed libs
from loguru import logger
from selenium.webdriver.chrome.options import Options

# project modules
from config import settings
from helpers.browsing import NewsBrowser
from helpers.util import output_excel_data


async def project(search_term):
    try:
        logger.info(f"Starting {settings.LOGGING_TITLE} project")


        news_browser = NewsBrowser(
            url="https://gothamist.com/search"
        )
        news_browser.open_browser()
        news_browser.screenshot()
        news_browser.search_articles(search_term)
        news_browser.close_browsers()


        # example_data = [
        #     {'Header1': 'Value1', 'Header2': 'Value4', 'Header3': 'Value7'},
        #     {'Header1': 'Value2', 'Header2': 'Value5', 'Header3': 'Value8'},
        #     {'Header1': 'Value3', 'Header2': 'Value6', 'Header3': 'Value9'},
        # ]

        # output_excel_data(
        #     path='../output/output.xlsx',
        #     data=example_data
        # )

    except Exception as e:
        logger.exception(f"Project failed to start, reason: {e}")
        raise


if __name__ == '__main__':
    asyncio.run(project("president"))
