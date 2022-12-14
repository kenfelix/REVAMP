from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
from pydantic import EmailStr
import requests
from config import settings
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from typing import List


def get_user_agent():
    return UserAgent(verify_ssl=False).random

@dataclass
class Scraper:
    driver: webdriver = None
    job_title_file: str = "/home/hp/Desktop/my_projects/Revamp/job_titles"
    
    def _get_job_title(self, file: str):
        try:
            with open(file=file) as my_file:
                string_file = my_file.read()
                list_file = string_file.split("\n")
        except:
            raise "could not open file"
        
        return list(set(list_file))
    
    def _get_sensible_title(self, title: str):
        list_title = title.lower().split(" ")
        if list_title[0] == "remote":
            new_title = " ".join([list_title[1], list_title[2]])
        else:
            new_title = " ".join([list_title[0], list_title[1], list_title[2]])
        return new_title.title()
        
    
    def _get_driver(self):
        if self.driver is None:
            user_agent = get_user_agent()
            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument(f"user-agent={user_agent}")
            # options.add_argument('--start-maximized')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_experimental_option("detach", True)
            driver = webdriver.Chrome(options=options)
            self.driver = driver
        return self.driver
    
    def _check_login(self, url: str):
        response = requests.get(url)
        return response.url != settings.redirect_url
    
    def _linkedin_login(self, email: EmailStr, password: str):
        login = self._check_login(url=settings.linkedin_home_url)
        if not login:
            driver = self._get_driver()
            driver.get(url=settings.linkedin_login_url)
            time.sleep(1)
            email_field = driver.find_element(by=By.ID, value="username")
            password_field = driver.find_element(by=By.ID, value="password")
            email_field.send_keys(settings.linkedin_email)
            password_field.send_keys(settings.linkedin_password)
            login_button = driver.find_element(by=By.XPATH, value="//button[@data-litms-control-urn=\"login-submit\"]")
            login_button.click()
            WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.ID, "global-nav")))
            print("Login Successful.")
        return
    
    def _scrape_linkedin_job_links(self, search_params: str) -> list:
        links: List = []
        driver = self._get_driver()
        driver.get(url=f"https://www.linkedin.com/jobs/search/?currentJobId=3366945039&keywords={search_params}")
        try:
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-tracking-control-name=\"public_jobs_dismiss\"]"))).click()
        except:
            pass
        
        print("scrapping links", end='\r')
        
        i = 1
        while i < 20:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1);")
            i += 1
            time.sleep(1)
            
            try:
                WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label=\"Load more results\"]"))).click()
                time.sleep(1)
            except:
                pass
                time.sleep(1)
                
        jobs_block = driver.find_element(by=By.CLASS_NAME, value="jobs-search__results-list")
        jobs_list = jobs_block.find_elements(by=By.CSS_SELECTOR, value="li")
        try:
            for job in jobs_list:
                all_links = job.find_elements(by=By.TAG_NAME, value="a")
                for a in all_links:
                    if "linkedin.com/jobs/view/" in str(a.get_attribute("href")):
                        links.append(a.get_attribute("href"))
                    else:
                        pass
        except:
            pass
        return links
        
       
    def  _scrape_linkedin_jobs_links(self):
        job_titles = self._get_job_title(self.job_title_file)
        links = []
        
        for title in job_titles:
            if title != '':
                new_link = self._scrape_linkedin_job_links(search_params=title)
                time.sleep(1)
                links.extend(new_link)
        return links
    
    def _get_requirements(self, job_desc: str):
        new_list = job_desc.lower().split("\n")
        word_list = ["requirements", "qualifications", "skills", "you are", "expectations", "what we are looking for", "required skills & qualifications",
                     "abilities", "what you bring to the table", "your profile", "qualifications and experience", "about you" "what we need from you?", "key skills/ experience required",
                     "basic requirements", "minimum qualifications", "skills and experience", "the minimum criteria is the following",
                     "Who we’re looking for", "qualifications & experience", "job requirements", "what you bring",
                     "requirements:", "qualifications:", "skills:", "you are:", "expectations:", "what we are looking for:", "required skills & qualifications:",
                     "abilities:", "what you bring to the table:", "your profile:", "qualifications and experience:", "about you:" "what we need from you:", "key skills/ experience required:",
                     "basic requirements:", "minimum qualifications:", "skills and experience:", "the minimum criteria is the following:",
                     "Who we’re looking for:", "qualifications & experience:", "job requirements:", "what you bring:",
                     ]
        final_list = []
        
        for i in range(len(new_list)):
            if new_list[i] == '' and new_list[i+1] in word_list and new_list[i+2] == '':
                new_index = i+3
        for i in range(new_index, len(new_list)):
            if  new_list[i] == '':
                break
            else:
                final_list.append(new_list[i])
            
        return final_list
        
    
    def _scarpe_link_info(self, link: str, link_index: int, links_len: int) -> dict:
        scraped_jobs = {}
        driver = self._get_driver()
        
        print(f"scrapping actual info\tlink(s) {link_index}/{links_len}", end="\r")
        try:
            driver.get(url=link)
            time.sleep(1)
            driver.find_element(by=By.XPATH, value="//button[@aria-label=\"Show more, visually expands previously read content above\"]").click()
            job_title = driver.find_element(by=By.XPATH, value="//h1[@class=\"top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title\"]").text
            job_title = self._get_sensible_title(title=job_title)
            job_info = driver.find_element(by=By.XPATH, value="//div[@class=\"show-more-less-html__markup\"]").text
            required_skills = self._get_requirements(job_info)
            
            
            scraped_jobs["job title"] = job_title
            scraped_jobs["required skills"] = required_skills
            
        except:
            pass
        
        return scraped_jobs
    
    def scrape_linkedin_jobs(self):
        jobs = []
        links = self._scrape_linkedin_jobs_links()
        
        for link in links:
            job = self._scarpe_link_info(link=link, link_index=links.index(link) + 1, links_len=len(links))
            jobs.append(job)
        
        new_jobs = list(filter(lambda x: x != {}, jobs))
            
        return new_jobs
        

    
    
    
    # scrape from indeed 
    # scrape from mustar 
    
     
        
