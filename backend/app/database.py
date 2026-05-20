from typing import Optional

from pymongo import ASCENDING, MongoClient
from pymongo.database import Database

from app.settings import settings

_client: Optional[MongoClient] = None

COLLECTIONS = [
    "raw_data",
    "cleaned_data",
    "predictions",
    "model_metrics",
    "products_snapshot",
]


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=3000)
    return _client


def get_database() -> Database:
    return get_client()[settings.mongo_database]


def ensure_indexes(db: Database) -> None:
    db.raw_data.create_index([("source", ASCENDING), ("product_id", ASCENDING)])
    db.cleaned_data.create_index([("product_id", ASCENDING), ("movement_date", ASCENDING)])
    db.predictions.create_index([("product_id", ASCENDING)], unique=True)
    db.model_metrics.create_index([("trained_at", ASCENDING)])
    db.products_snapshot.create_index([("product_id", ASCENDING)], unique=True)


def ping_database() -> bool:
    get_client().admin.command("ping")
    return True
