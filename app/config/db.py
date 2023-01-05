from pymongo import MongoClient

from .config import settings


def get_db():
    cluster = f"{settings.mongodb_uri}/?retryWrites=true&w=majority"

    client = MongoClient(cluster)
    db = client.revamp
    return db
