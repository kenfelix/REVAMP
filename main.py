from app.config.config import settings
from app.engine import s, scrape_links


def start_engine():
    # login = s.linkedin_login(email=settings.linkedin_email, password=settings.linkedin_password)
    # if login is False:
    #     s.close_driver()
    #     start_engine()
    scrape_links.delay("graphics")


if __name__ == "__main__":
    start_engine()
