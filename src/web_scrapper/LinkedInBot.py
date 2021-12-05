from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import logging
import pickle
import time
import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


class LinkedInBot:

    def __init__(self, delay=5):
        if not os.path.exists("data"):
            os.makedirs("data")
        log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(level=logging.INFO, format=log_fmt)
        self.delay = delay
        logging.info("Starting driver")
        self.driver = webdriver.Firefox()

    def login(self, email, password):
        """
        Logging-in to Linkedin
        """
        logging.info("Logging in")
        self.driver.maximize_window()
        self.driver.get('https://www.linkedin.com/login')
        time.sleep(self.delay)
        self.driver.find_elements(by=By.ID, value='username').send_keys(email)
        self.driver.find_elements(
            by=By.ID, value='password').send_keys(password)
        self.driver.find_elements(
            by=By.ID, value='password').send_keys(Keys.RETURN)
        time.sleep(self.delay)

    def search(self, keywords, location):
        """
        Enter Keywords in Search bar
        """
        logging.info("Search Jobs Page")
        self.driver.get("https://www.linkedin.com/jobs/")
        self.wait_for_element_ready(
            By.CLASS_NAME, 'jobs-search-box__text-input')
        time.sleep(self.delay)  # find the keywords/location search bars:
        search_bars = self.driver.find_elements(
            by=By.CLASS_NAME, value='jobs-search-box__text-input')
        search_keywords = search_bars[0]
        search_keywords.send_keys(keywords)
        search_location = search_bars[3]
        search_location.send_keys(location)
        time.sleep(self.delay)
        search_location.send_keys(Keys.RETURN)
        logging.info("Keywords Search Successful!!")
        time.sleep(self.delay)

    def wait(self, t_delay=None):
        """
        Just easier to build this in here.
        Parameters
        ----------
        t_delay [optional] : int
            seconds to wait.
        """
        delay = self.delay if t_delay == None else t_delay
        time.sleep(delay)

    def wait_for_element_ready(self, by, text):
        try:
            WebDriverWait(self.driver, self.delay).until(
                EC.presence_of_element_located((by, text)))
        except TimeoutException:
            logging.debug("wait_for_element_ready TimeoutException")
            pass

    def save_cookie(self, path):
        with open(path, 'wb') as filehandler:
            pickle.dump(self.driver.get_cookies(), filehandler)

    def load_cookie(self, path):
        with open(path, 'rb') as cookiesfile:
            cookies = pickle.load(cookiesfile)
            for cookie in cookies:
                self.driver.add_cookie(cookie)

    def scroll_to(self, job_list_item):
        """
        Just a function that will scroll to the list item in the column 
        """
        self.driver.execute_script(
            "arguments[0].scrollIntoView();", job_list_item)
        job_list_item.click()
        time.sleep(self.delay)

    def get_position_data(self, job):
        """
        Gets the position data for a posting.
        Parameters
        ----------
        job : Selenium webelement
        Returns
        -------
        list of strings : [position, company, location, details]
        """
        [position, company, location] = job.text.split('\n')[:3]
        details = self.driver.find_elements(by=By.ID, value="job-details")
        return [position, company, location, details]

    def close_session(self):
        """
        This function closes the actual session
        """
        logging.info("Closing Driver Session")
        self.driver.close()

    def run(self, email, password, keywords, location):
        if os.path.exists("data/cookies.txt"):
            self.driver.get("https://www.linkedin.com/")
            self.load_cookie("data/cookies.txt")
            self.driver.get("https://www.linkedin.com/")
        else:
            self.login(
                email=email,
                password=password
            )
            self.save_cookie("data/cookies.txt")

        logging.info("Begin LinkedIn Keyword Search")
        self.search(keywords, location)
        self.wait()

        # scrape pages,only do first 8 pages since after that the data isn't
        # well suited for me anyways:
        for page in range(2, 8):
            # get the jobs list items to scroll through:
            jobs = self.driver.find_elements(
                by=By.CLASS_NAME, value="occludable-update")
            for job in jobs:
                self.scroll_to(job)
                [position, company, location,
                    details] = self.get_position_data(job)
                print(position, company, location, details)
            # go to next page:
            bot.driver.find_elements(
                by=By.XPATH, value=f"//button[@aria-label='Page {page}']").click()
            bot.wait()
        logging.info("Done scraping.")
        logging.info("Closing DB connection.")
        bot.close_session()


if __name__ == "__main__":
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    bot = LinkedInBot()
    print(email, password)
    bot.run(email, password, "Software Developer", "United States")
