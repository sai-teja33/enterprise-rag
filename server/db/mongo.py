from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.core.config import settings

client = MongoClient(settings.MONGODB_URI)
db = client[settings.DB_NAME]

# collections
tenants_collection = db["tenants"]
documents_collection = db["documents"]
chunks_collection = db["document_chunks"]


def ping_mongodb():
    try:
        client.admin.command("ping")
        return True
    except ConnectionFailure:
        return False