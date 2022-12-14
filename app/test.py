from scraper import Scraper
from cleaned import Clean

s = Scraper(job_title_file="/home/hp/Desktop/my_projects/Revamp/software1.txt")


content = s.scrape_linkedin_jobs()

Clean(scraped_data=content).to_excel(file_name="Jobs", sheet_name="Software jobs")



