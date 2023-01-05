from app.config.config import settings
from app.engine import s, parse_key_words


def start_engine():
    # login = s.linkedin_login(email=settings.linkedin_email, password=settings.linkedin_password)
    # if login is False:
    #     s.close_driver()
    #     start_engine()
    parse_key_words.delay()


if __name__ == "__main__":
    start_engine()
