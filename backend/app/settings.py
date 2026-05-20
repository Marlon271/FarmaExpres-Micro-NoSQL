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
    inventory_service_url: str = os.getenv("INVENTORY_SERVICE_URL", "http://inventory-service:8082")
    inventory_service_timeout_ms: int = int(os.getenv("INVENTORY_SERVICE_TIMEOUT_MS", "5000"))
    jwt_secret: str = os.getenv(
        "JWT_SECRET",
        "mi_clave_super_secreta_ultra_segura_de_256_bits_minimo_1234567890",
    )
    environment: str = os.getenv("APP_ENV", os.getenv("ENVIRONMENT", "dev"))
    enable_dev_seed_endpoints: bool = os.getenv("ENABLE_DEV_SEED_ENDPOINTS", "true").lower() == "true"
    cors_origins: List[str] = None

    def __post_init__(self):
        origins = os.getenv(
            "BACKEND_CORS_ORIGINS",
            "http://localhost:5174,http://localhost:5173,http://127.0.0.1:5174",
        )
        object.__setattr__(self, "cors_origins", _split_origins(origins) or ["*"])


settings = Settings()
