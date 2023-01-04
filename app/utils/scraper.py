import json
import time
from dataclasses import dataclass, field
from math import ceil
from typing import List, Optional

from fake_useragent import UserAgent
from pydantic import EmailStr
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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
            options.add_argument("--no-sandbox")
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument(f"user-agent={user_agent}")
            # options.add_argument('--start-maximized')
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            options.add_experimental_option("detach", True)
            driver = webdriver.Chrome(options=options)
            self.driver = driver
        return self.driver

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
        WebDriverWait(driver, 100).until(
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

    def __get_requirements(self, raw_text: str):
        word_list = [
            "requirements",
            "qualifications",
            "skills",
            "you are",
            "expectations",
            "what we are looking for",
            "required skills",
            "abilities",
            "what you bring to the table",
            "your profile",
            "about you" "what we need from you?",
            "key skills",
            "basic requirements",
            "minimum qualifications",
            "skills and experience",
            "the minimum criteria is the following",
            "Who we’re looking for",
            "job requirements",
            "what you bring",
            "key competencies",
            "task",
            "will be a plus",
            "nice to have",
            "desired skills",
            "job knowledge",
            "other skills",
            "Would be great if you brought",
            "the ideal candidate",
        ]
        require_list = []

        doc = raw_text.lower().split("\n\n")

        for word in word_list:
            for sent in doc:
                if sent.startswith(word) and sent not in require_list:
                    require_list.append(sent)

        return "\n".join(require_list)

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
            job_type = (
                top_content.find_element(
                    by=By.CLASS_NAME, value="jobs-unified-top-card__job-insight"
                )
                .text.lower()
                .split(" · ")[-1]
            )
            job_info = driver.find_element(
                by=By.CLASS_NAME, value="jobs-description__content"
            ).text.lower()
            job_info = self.__get_requirements(raw_text=job_info).lower()
            if job_info != "":
                scraped_jobs["job title"] = job_title
                scraped_jobs["required skills"] = job_info
                scraped_jobs["experience level"] = job_type
                return scraped_jobs
        except:
            pass

        return None
