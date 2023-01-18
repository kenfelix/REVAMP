from app.engine import parse_key_words


def start_engine():
    parse_key_words.delay()


if __name__ == "__main__":
    start_engine()
