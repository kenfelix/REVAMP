import json
import re
import time
from dataclasses import dataclass, field
from math import ceil
from typing import List, Optional

from fake_useragent import UserAgent
from pydantic import EmailStr
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from ..config.config import settings


def get_user_agent():
    return UserAgent(verify_ssl=True).random


@dataclass
class Scraper:
    driver: webdriver = None

    def __get_driver(self):
        if self.driver is None:
            user_agent = get_user_agent()
            options = Options()
            options.binary_location = "/usr/bin/google-chrome-stable"
            options.add_argument("--no-sandbox")
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument(f"user-agent={user_agent}")
            # options.add_argument('--start-maximized')
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            options.add_experimental_option("detach", True)
            driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()), options=options
            )
            self.driver = driver
        return self.driver

    def close_driver(self):
        self.__get_driver().quit()

    def linkedin_login(self, email: EmailStr, password: str):
        driver = self.__get_driver()
        driver.get(url=settings.linkedin_login_url)
        time.sleep(1)
        email_field = driver.find_element(by=By.ID, value="username")
        password_field = driver.find_element(by=By.ID, value="password")
        email_field.send_keys(email)
        password_field.send_keys(password)
        login_button = driver.find_element(
            by=By.XPATH, value='//button[@data-litms-control-urn="login-submit"]'
        )
        login_button.click()
        print(driver.current_url)
        # if driver.current_url == "https://www.linkedin.com/error_pages/unsupported-browser.html":
        #     return False
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "global-nav"))
        )
        print("Login Successful.")
        with open("cookies.json", "w") as f:
            json.dump(driver.get_cookies(), f)
        return

    def scrape_linkedin_job_links(self, search_params: str) -> list:
        links: List = []
        driver = self.__get_driver()
        driver.get("https://www.linkedin.com/feed")
        with open("cookies.json", "r") as f:
            cookies = json.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.get(
            url=f"https://www.linkedin.com/jobs/search/?currentJobId=3366945039&keywords={search_params}"
        )
        try:
            job_count = driver.find_element(
                by=By.XPATH,
                value='//div[@class="jobs-search-results-list__title-heading"]/small',
            ).text
            job_count = int(job_count.split(" ")[0].replace(",", ""))
            pages = ceil(job_count / 25)
        except:
            pass

        try:
            for page in range(1, (pages + 1)):
                print(f"collecting the links in page {page}")
                jobs_block = driver.find_element(
                    by=By.CLASS_NAME, value="jobs-search-results-list"
                )
                jobs_list = jobs_block.find_elements(by=By.CSS_SELECTOR, value="li")

                for job in jobs_list:
                    all_links = job.find_elements(by=By.TAG_NAME, value="a")
                    for a in all_links:
                        if (
                            "linkedin.com/jobs/view/" in str(a.get_attribute("href"))
                            and a.get_attribute("href") not in links
                        ):
                            links.append(a.get_attribute("href"))
                        else:
                            pass

                    driver.execute_script("arguments[0].scrollIntoView();", job)

                driver.find_element(
                    by=By.XPATH, value=f'//button[@aria-label="Page {page+1}"]'
                ).click()
                time.sleep(1)
        except:
            pass
        return links

    def __find_start_end_words(self, text: str, start_words: list, end_words: list):
        start_pattern = "|".join(start_words)
        end_pattern = "|".join(end_words)

        start_match = re.search(start_pattern, text)
        if start_match:
            start_index = start_match.start()
            end_match = re.search(end_pattern, text[start_index:])
            if end_match:
                end_index = end_match.start() + start_index
                return (start_match.group(), end_match.group())
            else:
                return (start_match.group(), None)
        else:
            return (None, None)

    def __get_text_between(self, text: str, start: str, end: str):
        if start is not None and end is not None:
            pattern = re.compile(f"{start}(.*?){end}", re.DOTALL)
        else:
            pattern = re.compile(f"{start}(.*)", re.DOTALL)
        return pattern.search(text).group(1)

    def __get_requirements(self, text: str):
        with open("start_words.txt", "r") as doc:
            start_string_words = doc.read()
        start_words = start_string_words.split("\n")

        with open("end_words.txt", "r") as doc:
            end_string_words = doc.read()
        end_words = end_string_words.split("\n")

        (start, end) = self.__find_start_end_words(
            text=text, start_words=start_words, end_words=end_words
        )

        if start is None and end is None:
            requirement = ""
        elif start is None and end is not None:
            requirement = ""
        else:
            requirement = self.__get_text_between(text=text, start=start, end=end)
            if start in requirement or end in requirement:
                requirement = requirement.replace(start, "").replace(end, "")
        return requirement

    def scarpe_link_info(self, link: str) -> Optional[dict]:
        scraped_jobs = {}
        job_type = "associate"
        driver = self.__get_driver()
        driver.get("https://www.linkedin.com/feed")

        with open("cookies.json", "r") as f:
            cookies = json.load(f)
        try:
            for cookie in cookies:
                driver.add_cookie(cookie)
        except:
            pass

        try:
            driver.get(url=link)
            time.sleep(1)
            driver.find_element(by=By.CLASS_NAME, value="artdeco-card__actions").click()
            top_content = driver.find_element(by=By.XPATH, value='//div[@class="p5"]')
            job_title = top_content.find_element(
                by=By.TAG_NAME, value="h1"
            ).text.lower()
            job_types = (
                top_content.find_element(
                    by=By.CLASS_NAME, value="jobs-unified-top-card__job-insight"
                )
                .text.lower()
                .split(" · ")
            )
            if len(job_types) > 1:
                job_type = job_types[-1]
            else:
                job_type = "associate"
            job_info = driver.find_element(
                by=By.CLASS_NAME, value="jobs-description__content"
            ).text.lower()
            job_requirement = self.__get_requirements(text=job_info).lower()
            if job_info != "":
                scraped_jobs["job_title"] = job_title
                scraped_jobs["experience_level"] = job_type
                scraped_jobs["skills"] = job_requirement
                return scraped_jobs
        except:
            pass

        return None
