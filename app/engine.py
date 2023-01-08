from app.utils.cleaned import Clean
from app.utils.db import insert_job
from app.utils.scraper import Scraper

from .celery import app

s = Scraper()
c = Clean()


@app.task
def parse_key_words():
    string_words = ""
    with open("search_parameters.txt", "r") as doc:
        string_words = doc.read()
    words = string_words.split("\n")
    for word in words:
        scrape_links.delay(word)


@app.task
def scrape_links(search_params: str):
    links = s.scrape_linkedin_job_links(search_params=search_params)
    scrape_info_from_link.delay(links)


@app.task
def scrape_info_from_link(links: list):
    for link in links:
        new_raw_job = s.scarpe_link_info(link=link)
        if new_raw_job is None:
            pass
        else:
            clean.delay(new_raw_job)


@app.task
def clean(raw_job: dict):
    new_dict = {}
    industry = raw_job.get("industry")
    title = c.clean_title(raw_title=raw_job.get("job_title"))
    experience_level = raw_job.get("experience_level")
    skills = c.clean_skills(raw_text=raw_job.get("skills"))
    if skills != []:
        new_dict["industry"] = industry
        new_dict["job_title"] = title
        new_dict["experience_level"] = experience_level
        new_dict["skills"] = skills
        store_in_db.delay(new_dict)
    return None


@app.task
def store_in_db(job: dict):
    insert_job(job)
