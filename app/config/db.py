from pymongo import MongoClient


def get_db():
    cluster = "mongodb+srv://sonofzion:12345@crypto-town.otgt6mb.mongodb.net/?retryWrites=true&w=majority"

    client = MongoClient(cluster)
    db = client.revamp
    return db
