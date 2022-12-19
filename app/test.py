from cleaned import Clean
from config import settings
from scraper import Scraper

s = Scraper(job_title_file="/home/hp/Desktop/my_projects/Revamp/software1.txt")
c = Clean()


# s.linkedin_login(email=settings.linkedin_email, password=settings.linkedin_password)
# links = s.scrape_linkedin_job_links(search_params="graphics")
# for link in links:
#     raw_job = s.scarpe_link_info(link=link, link_index=links.index(link) + 1, links_len=len(links))
#     if raw_job is None:
#         continue
#     title = c.clean_title(raw_title=raw_job.get("job title"))
#     skills = c.clean_skills(raw_text=raw_job.get("required skills"))
#     print(title, skills)

title = c.clean_title(raw_title="Senior Product Designer")
print(title)
