import os
from dataclasses import dataclass
from typing import List


def _split_origins(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongo_database: str = os.getenv("MONGO_DATABASE", "farmaexpres_predictions")
    relational_db_url: str = os.getenv("RELATIONAL_DB_URL", "")
    cors_origins: List[str] = None

    def __post_init__(self):
        origins = os.getenv(
            "BACKEND_CORS_ORIGINS",
            "http://localhost:5174,http://localhost:5173,http://127.0.0.1:5174",
        )
        object.__setattr__(self, "cors_origins", _split_origins(origins) or ["*"])


settings = Settings()
