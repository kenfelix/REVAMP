from app.utils.cleaned import Clean
from app.utils.db import insert_job
from app.utils.scraper import Scraper

from .celery import app

s = Scraper()
c = Clean()

@app.task
def scrape_links(search_params: str):
    links = s.scrape_linkedin_job_links(search_params=search_params)
    scrape_info_from_links.delay(links)


@app.task
def scrape_info_from_links(links: list):
    for link in links:
        new_raw_job = s.scarpe_link_info(link=link)
        if new_raw_job is None:
            pass
        else:
            clean.delay(new_raw_job)


@app.task
def clean(raw_job: dict):
    new_dict = {}
    title = c.clean_title(raw_title=raw_job.get("job title"))
    rate = raw_job.get("experience level")
    skills = c.clean_skills(raw_text=raw_job.get("required skills"))
    if skills != []:
        new_dict["job title"] = title
        new_dict["experience level"] = rate
        new_dict["required skills"] = skills
        store_in_db.delay(new_dict)
    return None


@app.task
def store_in_db(job: dict):
    insert_job(job)
