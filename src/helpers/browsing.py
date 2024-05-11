# built ins
import re
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Callable

# installed libs
from RPA.Browser.Selenium import (
    Selenium,
    WebDriverWait,
    expected_conditions as EC,
    By
)
from RPA.HTTP import HTTP
from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.remote.webdriver import WebElement
from selenium.common.exceptions import NoSuchElementException

# project modules
from config import settings
from logger import Logger
from helpers.util import (
    wait_and_retrieve_item,
    interact_with_element,
    extract_date
)


class NewsBrowser(object):
    def __init__(self, logger: Logger):
        # no try-except here because parent wrapped in try catch and will log
        # and crash there if something goes wrong here
        self.browser = Selenium()
        self.logger = logger
        self.ENV = settings.ENV
        self.logger.info("NewsBrowser initialized")
        self.RPA_HTTP = HTTP()

    # defining open and close methods separately to re-initialize on crashes

    def open_browser(self, url):
        try:
        
            # options for the headless browser
            options = webdriver.ChromeOptions()
            # local usage
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            # TODO: apply these options to the browser for robocloud too
            # popup blocking
            options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.notifications": 2
            })
            # using WSL locally with headless chrome so want to be able to have
            # this work locally and in the cloud based on options
            if self.ENV == "local":
                service = webdriver.ChromeService(
                    executable_path="/usr/bin/chromedriver",
                    log_output="../logs/chrome_driver.log"
                )

                driver = webdriver.Chrome(options=options, service=service)
                driver_id = self.browser.register_driver(driver, "my_driver")
                self.browser.switch_browser(driver_id)
            else:
                self.browser.open_available_browser(options=options)
            
            # setting a specific size for consistent handling
            self.browser.set_window_size(1024, 768)
            self.browser.go_to(url)


        except Exception as e:
            self.logger.exception(f"Failed to open browser, reason: {e}")
            raise Exception("failed to open browser")

    def close_browsers(self):
        try:
            self.browser.close_all_browsers()
        except Exception as e:
            self.logger.exception(f"Failed to close browser, reason: {e}")
            raise Exception(
                "Failed to close browser - see above for error info")
    
    def load_more_cards(self):
        try:
            button_path = "//button/span[contains(text(), 'Load More')]"
            # TODO: move queries over to xpath like this
            load_more_button: WebElement = wait_and_retrieve_item(
                self.logger,
                driver=self.browser.driver,
                expected_condition=EC.presence_of_element_located,
                by=By.XPATH,
                identifier=button_path
            )

            _: WebElement = wait_and_retrieve_item(
                self.logger,
                driver=self.browser.driver,
                expected_condition=EC.element_to_be_clickable,
                by=By.XPATH,
                identifier=button_path
            )

            
            interact_with_element(
                logger=self.logger,
                element_interaction=load_more_button.click
            )

            # this loads very quickly so just loop through all of them until no
            # more cards before starting processing
            time.sleep(settings.DEFAULT_SLEEP)
        
        except NoSuchElementException:
            self.logger.info("No more cards to load.")
        except Exception as e:
            self.screenshot("load_more_cards_error")
            self.logger.exception(
                f"Failed to load more cards, reason: {e}")
            raise Exception(
                "Failed to load more cards - see above for error info")

    # TODO: docstrings
    def search_articles(
            self,
            output_sub_dir: str,
            query: str,
            months: int = 1
        ):
        """
        Search for articles on the Gothamist website based on the query"""
        try:
            self.logger.info("entering search function")

            search_bar: WebElement = wait_and_retrieve_item(
                self.logger,
                driver=self.browser.driver,
                expected_condition=EC.presence_of_element_located,
                by=By.CLASS_NAME,
                identifier="search-page-input"
            )
            
            interact_with_element(
                logger=self.logger,
                element_interaction=search_bar.click
            )
            interact_with_element(
                logger=self.logger,
                element_interaction=search_bar.send_keys,
                params=[query]
            )

            # TODO: look at defaulting this duration
            interact_with_element(
                logger=self.logger,
                element_interaction=search_bar.send_keys,
                params=[keys.Keys.ENTER]
            )

            articles: WebElement = wait_and_retrieve_item(
                self.logger,
                driver=self.browser.driver,
                expected_condition=EC.presence_of_element_located,
                by=By.ID,
                identifier="resultList"
            )
            
            cards: WebElement = wait_and_retrieve_item(
                self.logger,
                driver=articles,
                expected_condition=EC.presence_of_all_elements_located,
                by=By.CLASS_NAME,
                identifier="gothamist-card"
            )
            cards_length = len(cards)

            # TODO: extract this into a function so we can load more and
            # continue from the given index
            output_data = []
            index = 0
            latest_date = datetime.now()
            articles_start_date = latest_date - relativedelta(months=months)

            self.logger.info("going through cards")

            # for card in cards:
            # TODO: while months not equal to max months and there are still
            # new cards coming in with load more (note gothamist does seem to
            # have a max of 100 articles for a search - relay this info
            # in the return data
            fresh_retrieval = True
            while latest_date > articles_start_date and index < cards_length:
                if fresh_retrieval:
                # #     # TODO: add in a fail response here where we process the
                # #     # rest of the cards we have if load more fails and try
                # #     # again later (or potentially refresh page)
                    self.load_more_cards()
                    fresh_retrieval = False

                
                    # request up to 10 times in 1 second intervals if if doesn't
                    # respond immediately, else gracefully exit and TODO: make a note
                    # of this in in the output file

                    
                    # TODO: every time we hit the index of max card, retrieve
                    # cards so we can do the while check expression 
                        

                card = cards[index]
                index += 1
                self.logger.info(f"on card {index}")

                # TODO: if fresh retrieval click load more and continue (so we can get new cards immediately by the time this is done - also look at adding in a timer duration after anyways - so like request every 2 seconds for 10 attempts as this should give us enough time, also consider checking site loading errors here)

                # TODO: start a try except here where we continue with other
                # cards if it fails to respond

                article_details = {}

                # retrieve the image url
                # TODO: download the image via asyncio or whatever works for robocloud in the background
                image_url: WebElement = wait_and_retrieve_item(
                    self.logger,
                    driver=card,
                    expected_condition=EC.presence_of_element_located,
                    by=By.CSS_SELECTOR,
                    identifier=".image.native-image.prime-img-class"
                ).get_attribute('src')
                article_details["image_url"] = image_url
                self.browser.execute_javascript(f"window.open('{image_url}');")
                
                self.browser.driver.switch_to.window(
                    self.browser.driver.window_handles[-1])
                
        
                # get the image name after the url redirect (need to load the
                # page to get the image name)
                try:
                    WebDriverWait(self.browser.driver, 10).until(
                        lambda driver: driver.current_url != 'about:blank'
                    )
                except:
                    self.logger.info(
                        "Could not retrieve image name for this card"
                        )
                if self.browser.driver.current_url == 'about:blank':
                    img_name = "failed to retrieve image name"
                else:
                    img_name = self.browser.driver.current_url.split(
                    'https://images-prod.gothamist.com/images/', 1)[1]
                    
                    self.RPA_HTTP.download(
                        image_url,
                        f"{settings.OUTPUT_PATH}/{output_sub_dir}/{img_name}"
                    )


                article_details["image_name"] = img_name

                self.browser.driver.close()
                self.browser.driver.switch_to.window(
                    self.browser.driver.window_handles[0])

                
                # we load the article and image url as early as possible here
                # so that we can get to them after the rest of the processing
                # because it takes a while to load in the date (happens after
                # everything else is done)
                article_link: WebElement = wait_and_retrieve_item(
                    self.logger,
                    driver=card,
                    expected_condition=EC.presence_of_element_located,
                    by=By.CLASS_NAME,
                    identifier="image-with-caption-image-link"
                ).get_attribute('href')
                self.browser.execute_javascript(
                    f"window.open('{article_link}');")


                title: WebElement = wait_and_retrieve_item(
                    self.logger,
                    driver=card,
                    expected_condition=EC.presence_of_element_located,
                    by=By.CLASS_NAME,
                    identifier="h2"
                ).text
                

                article_details["title"] = title

                description: WebElement = wait_and_retrieve_item(
                    self.logger,
                    driver=card,
                    expected_condition=EC.presence_of_element_located,
                    by=By.CLASS_NAME,
                    identifier="desc"
                ).text
                

                article_details["description"] = description

                combined_title_description = title + description

                search_phrase_count = combined_title_description.count(query)
                article_details["search_phrase_count"] = search_phrase_count

                money_regex = r"\$\d+(,\d{3})*(\.\d{1,2})?|\d+ dollars|\d+ USD"

                money_value_present = bool(
                    re.search(money_regex, combined_title_description))

                article_details["money_value_present"] = money_value_present

                # go and get the details of the article page we opened earlier
                self.browser.driver.switch_to.window(
                    self.browser.driver.window_handles[-1])
                # get the image name after the url (need to load the page to
                # get the image name)
                date_published_element: WebElement = wait_and_retrieve_item(
                    self.logger,
                    driver=self.browser.driver,
                    expected_condition=EC.presence_of_element_located,
                    by=By.CSS_SELECTOR,
                    identifier=".date-published p.type-caption"
                )

                _ = wait_and_retrieve_item(
                    self.logger,
                    driver=self.browser.driver,
                    expected_condition=EC.text_to_be_present_in_element,
                    by=By.CSS_SELECTOR,
                    identifier=".date-published p.type-caption",
                    additional_params=[date_published_element.text]
                )


                date_published = date_published_element.get_attribute(
                    "textContent")

                article_details["date_published"] = extract_date(
                    logger=self.logger,
                    published_string=date_published
                )
                
                self.browser.driver.close()
                self.browser.driver.switch_to.window(
                    self.browser.driver.window_handles[0])
                
                
                latest_date = article_details["date_published"]

                if latest_date > articles_start_date:
                    output_data.append(article_details)

                if index == cards_length:
                    new_card_request_count = 0
                    while True:
                        cards: WebElement = wait_and_retrieve_item(
                            self.logger,
                            driver=articles,
                            expected_condition=EC.presence_of_all_elements_located,
                            by=By.CLASS_NAME,
                            identifier="gothamist-card"
                        )

                        new_cards_length = len(cards)

                        if new_cards_length > cards_length:
                            fresh_retrieval = True
                            cards_length = new_cards_length
                            break

                        new_card_request_count += 1
                        time.sleep(1)
                
            self.logger.info(f"search complete for {query}")

            return output_data

        except Exception as e:
            self.logger.exception(
                f"Failed to search for articles, reason: {e}")
            raise Exception(
                "Failed to search for articles - see above for error info")

    def screenshot(self, title: str = f"{settings.PROJECT_TITLE}-screenshot"):
        try:
            timestamp = datetime.now()
            path = f"{settings.SCREENSHOT_FOLDER_PATH}/{title}-{timestamp}.png"
            self.browser.screenshot(
                filename=path
            )
        except Exception as e:
            self.logger.exception(f"Failed to take screenshot, reason: {e}")
            raise Exception(
                "Failed to take screenshot - see above for error info")
