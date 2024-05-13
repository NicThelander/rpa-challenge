# built ins
from datetime import datetime
import re
import time
from typing import Any, Callable, Dict, List, Union

# installed libs
import pandas as pd
from RPA.Browser.Selenium import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from RPA.Browser.Selenium import (
    Selenium,
    WebDriverWait,
    expected_conditions as EC,
    By
)

# project modules
from logger import Logger
from config import settings


def output_excel_data(logger: Logger, path: str, data: List[Dict[str, str]]) -> None:
    """Attempts to output data to an excel file
    
    #### Parameters
    ------
    1. logger : Logger
        - logger instance
    2. path : str
        - path to the excel file
    3. data : List[Dict[str, str]]
        - data to be output to the excel file
    
    #### Returns
    ------
        - None
    
    #### Raises
    ------
        - Exception
            - when failing to output data to excel
    """
    try:
        df = pd.DataFrame(data)
        df.to_excel(path, index=False)
    except Exception as e:
        logger.exception(f"Failed to output data to excel, reason: {e}")
        raise Exception(
            "Failed to output data to excel - see above for error info"
        )

def wait_and_retrieve_item(
    logger: Logger,
    driver: WebDriver,
    expected_condition: Callable,
    by: str,
    identifier: str,
    additional_params: List[Any] = [],
    timeout=settings.DEFAULT_TIMEOUT,
    sleep_duration=settings.DEFAULT_SLEEP
) -> Union[WebElement, List[WebElement]]:
    """Attempts to find the element(s) based on the expected condition and
    locator. a default timeout of 20 seconds and sleep to simulate human delay
    of 0.2 seconds are used.

    #### Parameters
    ------
    1. logger : Logger
        - logger instance
    2. driver : WebDriver
        - selenium webdriver instance
    3. expected_condition : Callable
        - function used for location
            (from RPA.Browser.Selenium.expected_conditions)
    4. by : str
        - method of location (from RPA.Browser.Selenium.By)
    5. identifier : str
        - identifier for location (e.g. class name, id, etc.)
    6. additional_params : List[Any], (default [])
        - additional params for the expected condition
    7. timeout : int, (default defined at settings.DEFAULT_TIMEOUT)
        - timeout duration waiting for element
    8. sleep_duration : float, (default defined at settings.DEFAULT_SLEEP)
        - time to sleep after element is located (to simulate human delay)

    #### Returns
    ------
    - Union[Callable[[WebDriver], WebElement], Callable[[WebDriver],
        List[WebElement]]]
        - Callable that takes a WebDriver and returns a WebElement or a List
            of WebElements

    #### Raises
    ------
    - ValueError
        - when failing to locate element
    """
    try:
        element: Union[
            Callable[[WebDriver], WebElement],
            Callable[[WebDriver], List[WebElement]]
        ] = WebDriverWait(driver, timeout).until(
            expected_condition(
                (by, identifier), *additional_params)
        )
        time.sleep(sleep_duration)
        return element
    except Exception as e:
        logger.exception(f"Failed to locate element, reason: {e}")
        raise Exception(
            f"Failed to locate element - see above for error info"
        )

def interact_with_element(
    logger: Logger,
    driver: WebDriver,
    element_interaction: Callable,
    params: List[Any] = [],
    sleep_duration=settings.DEFAULT_SLEEP
) -> None:
    """Attempts to interact with the element(s) based on the
    element_interaction - useful because we bake in a sleep to emulate human
    delay. Also attempts to close any popups that close via checking if the class they use for the close button is present on the page.

    #### Parameters
    ------
    1. logger : Logger
        - logger instance
    1. driver : WebDriver
        - selenium webdriver instance
    2. element_interaction : Callable
        - function used to interact with the element
            (for eg search_bar.click())s.DEFAULT_TIMEOUT)
        - timeout duration waiting for element
    3. sleep_duration : float, (default defined at settings.DEFAULT_SLEEP)
        - time to sleep after element is located (to simulate human delay)

    #### Returns
    ------
    - None
        - interacts with the web element

    #### Raises
    ------
        - Exception
            - when failing to interact with the element
    """
    try:
        close_button = WebDriverWait(driver, 0.1).until(
            EC.presence_of_element_located(
                (By.XPATH, '//button[@title="Close"]')
                # (By.CLASS_NAME, "dillcity-CloseButton")
                )
        )
        
        close_button.click()
    except TimeoutException:
        # Popup is not present, do nothing
        pass
    except NoSuchElementException:
        # Popup is not present, do nothing
        pass
    except Exception as e:
        # We just want to close popups here, we don't actually care
        # if there is an error
        pass
    try:
        element_interaction(*params)
        time.sleep(sleep_duration)
    except Exception as e:
        logger.exception(f"Failed to interact with element, reason: {e}")
        raise Exception(
            "Failed to interact with element - see above for error info"
        )

def extract_date(logger: Logger, published_string: str) -> datetime:
    """Attempts to extract the date from the published string
    
    #### Parameters
    ------
    1. logger : Logger
        - logger instance
    2. published_string : str
    - string containing the date
    
    #### Returns
    ------
        - datetime
            - datetime object of the date extracted from the string
        
    #### Raises
    ------
        - Exception
            - when failing to extract the date from the string
    """
    try: 
        # Extract the date string
        match = re.search(r'Published (.*?)( at|$)', published_string)
        if match:
            date_string = match.group(1)
            # Parse the date string into a datetime object with known formats
            try:
                date = datetime.strptime(date_string, '%B %d, %Y')
            except ValueError:
                date = datetime.strptime(date_string, '%b %d, %Y')
            return date
        else:
            raise Exception('Failed to extract date from string')
    except Exception as e:
        logger.exception(f"Failed to extract date from string, reason: {e}")
        raise Exception(
            "Failed to extract date from string - see above for error info"
        )
