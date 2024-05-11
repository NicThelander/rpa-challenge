import re
import time
from RPA.Browser.Selenium import Selenium, WebDriverWait, expected_conditions as EC, By
from selenium import webdriver
from selenium.webdriver.common import keys
from loguru import logger


class NewsBrowser(object):
    def __init__(self, url, options = None):
        self.url = url
        self.browser = Selenium()
        self.options = options

    # defining open and close methods separately to re-initialize on crashes
    def open_browser(self):
        # using WSL locally with headless chrome so want to be able to have this work locally and in the cloud based on options
        # if self.options:
        # options for the headless browser
        options = webdriver.ChromeOptions()
        options.add_argument("--headless") 
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # options.add_argument('--user-data-dir=./data')

        service = webdriver.ChromeService("/usr/bin/chromedriver", log_output="chrome_driver.log")
        driver = webdriver.Chrome(options=options, service=service)
        driver_id = self.browser.register_driver(driver, "my_driver")
        self.browser.switch_browser(driver_id)
        self.browser.set_window_size(1024, 768)
        self.browser.go_to(self.url)
        # else:
        #     self.browser.open_available_browser(self.url)
        
        # setting a specific size for consistent handling

    def close_browsers(self):
        self.browser.close_all_browsers()

    def search_articles(self, query):
        try:
            logger.info("entering search function")
            default_timeout = 20
            default_sleep = 0.5

            # gothamist
            search_bar = WebDriverWait(self.browser.driver, default_timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, "search-page-input"))
            )
            time.sleep(default_sleep)
            search_bar.click()
            self.screenshot()
            search_bar.send_keys(query)
            time.sleep(default_sleep)
            search_bar.send_keys(keys.Keys.ENTER)

            articles = WebDriverWait(self.browser.driver, default_timeout).until(
                EC.presence_of_element_located((By.ID, "resultList"))
            )

            cards = WebDriverWait(articles, default_timeout).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "gothamist-card"))
            )
            
            # TODO: extract this into a function so we can load more and continue from the given index
            output_objects = []
            count = 0
            
            logger.info("going through cards")
            for card in cards:
                count += 1
                logger.info(f"on card {count}")
                article_details = {}

                image_url = WebDriverWait(card, default_timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".image.native-image.prime-img-class"))
                ).get_attribute('src')
                article_details["image_url"] = image_url

                self.browser.execute_javascript(f"window.open('{image_url}');")
                self.browser.driver.switch_to.window(self.browser.driver.window_handles[-1])
                # get the image name after the url (need to load the page to get the image name)
                image_name = self.browser.driver.current_url.split('https://images-prod.gothamist.com/images/', 1)[1]
                article_details["image_name"] = image_name
                self.browser.driver.close()
                self.browser.driver.switch_to.window(self.browser.driver.window_handles[0])

                article_link = WebDriverWait(card, default_timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "image-with-caption-image-link"))
                ).get_attribute('href')
                # TODO: get date from article
                self.browser.execute_javascript(f"window.open('{article_link}');")
                self.browser.driver.switch_to.window(self.browser.driver.window_handles[-1])
                # get the image name after the url (need to load the page to get the image name)
                date_published_element = WebDriverWait(self.browser.driver, default_timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".date-published p.type-caption"))
                )

                WebDriverWait(self.browser.driver, default_timeout).until(
                    EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".date-published p.type-caption"), date_published_element.text)
                )

                date_published = date_published_element.get_attribute("textContent")
                
                article_details["date_published"] = date_published
                self.browser.driver.close()
                self.browser.driver.switch_to.window(self.browser.driver.window_handles[0])

                title = WebDriverWait(card, default_timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "h2"))
                ).text
                article_details["title"] = title

                description = WebDriverWait(card, default_timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "desc"))
                ).text
                article_details["description"] = description

                combined_title_description = title + description

                search_phrase_count = combined_title_description.count(query)
                article_details["search_phrase_count"] = search_phrase_count

                money_pattern = r"\$\d+(,\d{3})*(\.\d{1,2})?|\d+ dollars|\d+ USD"

                money_value_present = bool(re.search(money_pattern, combined_title_description))

                article_details["money_value_present"] = money_value_present

            
                output_objects.append(article_details)

                
            pass

                
        except Exception as e:
            logger.exception(f"Failed to search for articles, reason: {e}")
            raise
            
    
    def screenshot(self):
        self.browser.screenshot()

