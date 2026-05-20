from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.auth import AuthContext, ensure_dev_seed_enabled, require_roles
from app.database import COLLECTIONS, ensure_indexes, get_database, ping_database
from app.services.cleaning import clean_records
from app.services.ingestion import ingest_from_inventory_snapshot, ingest_from_postgres, replace_generated_data
from app.services.inventory_client import fetch_inventory_snapshot
from app.services.prediction import build_predictions
from app.settings import settings


class IngestRequest(BaseModel):
    source: str = Field(default="inventory", pattern="^(generated|postgres|inventory)$")
    product_count: int = Field(default=80, ge=1, le=200)
    days: int = Field(default=180, ge=15, le=730)


class TrainRequest(BaseModel):
    horizon_days: int = Field(default=7, ge=1, le=60)


app = FastAPI(
    title="FarmaExpres Prediction Service",
    version="0.2.0",
    description="Microservicio de analítica predictiva con MongoDB, limpieza de datos e integración con inventory-service.",
)
router = APIRouter(prefix="/api/predictions", tags=["Predictions"])

ADMIN_AUDITOR = require_roles("ADMIN", "AUDITOR")
READ_ROLES = require_roles("ADMIN", "AUDITOR", "FARMACEUTICO")
ADMIN_ONLY = require_roles("ADMIN")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    ensure_indexes(get_database())


def _serialize(value: Any) -> Any:
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    return value


def _latest_metrics(db, metric_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
    query = {"type": metric_type} if metric_type else {}
    metrics = db.model_metrics.find_one(query, sort=[("trained_at", -1)])
    return _serialize(metrics) if metrics else None


def _health_response() -> Dict[str, Any]:
    try:
        mongo_ok = ping_database()
        db = get_database()
        counts = {collection: db[collection].count_documents({}) for collection in COLLECTIONS}
    except Exception as exc:  # pragma: no cover - defensive health response
        return {"status": "degraded", "mongo": False, "error": str(exc)}
    ready_to_clean = counts["raw_data"] > 0
    ready_to_train = counts["cleaned_data"] > 0
    return {
        "status": "ok",
        "mongo": mongo_ok,
        "database": settings.mongo_database,
        "counts": counts,
        "pipeline": {
            "ready_to_clean": ready_to_clean,
            "ready_to_train": ready_to_train,
            "has_predictions": counts["predictions"] > 0,
        },
    }


def _seed_test_data(request: IngestRequest = IngestRequest()) -> Dict[str, Any]:
    db = get_database()
    result = replace_generated_data(db, product_count=request.product_count, days=request.days)
    return _serialize({"message": "Datos de prueba generados en MongoDB.", **result})


def _ingest(request: IngestRequest = IngestRequest(), context: AuthContext | None = None) -> Dict[str, Any]:
    db = get_database()
    if request.source == "inventory":
        if context is None:
            raise HTTPException(status_code=401, detail="Token JWT requerido para ingestar desde inventory-service.")
        result = ingest_from_inventory_snapshot(db, fetch_inventory_snapshot(context))
    elif request.source == "postgres":
        result = ingest_from_postgres(db, settings.relational_db_url)
        if result["source"] == "generated":
            result["warning"] = "RELATIONAL_DB_URL no está configurada; se cargaron datos generados."
    else:
        result = replace_generated_data(db, product_count=request.product_count, days=request.days)
    return _serialize({"message": "Ingesta finalizada.", **result})


def _clean() -> Dict[str, Any]:
    db = get_database()
    raw_records = list(db.raw_data.find({}))
    if not raw_records:
        raise HTTPException(status_code=400, detail="No hay datos crudos. Ejecuta /ingest o /seed-test-data.")

    cleaned_records, metrics = clean_records(raw_records)
    db.cleaned_data.delete_many({})
    if cleaned_records:
        db.cleaned_data.insert_many(cleaned_records)

    db.model_metrics.insert_one({"type": "cleaning", **metrics, "trained_at": datetime.utcnow()})
    return _serialize({"message": "Limpieza finalizada.", **metrics})


def _train(request: TrainRequest = TrainRequest()) -> Dict[str, Any]:
    db = get_database()
    cleaned_records = list(db.cleaned_data.find({}))
    if not cleaned_records:
        raise HTTPException(status_code=400, detail="No hay datos limpios. Ejecuta /clean primero.")

    snapshots = list(db.products_snapshot.find({}))
    predictions, metrics = build_predictions(cleaned_records, snapshots, horizon_days=request.horizon_days)

    db.predictions.delete_many({})
    if predictions:
        db.predictions.insert_many(predictions)
    db.model_metrics.insert_one({"type": "training", **metrics})

    return _serialize({"message": "Modelo recalculado.", "metrics": metrics})


def _list_predictions(limit: int = 50) -> List[Dict[str, Any]]:
    db = get_database()
    cursor = db.predictions.find({}).sort("predicted_demand_units", -1).limit(max(1, min(limit, 200)))
    return _serialize(list(cursor))


def _get_prediction(product_id: str) -> Dict[str, Any]:
    db = get_database()
    prediction = db.predictions.find_one({"product_id": product_id})
    if not prediction:
        raise HTTPException(status_code=404, detail="Predicción no encontrada para el producto solicitado.")
    return _serialize(prediction)


def _metrics() -> Dict[str, Any]:
    db = get_database()
    latest = _latest_metrics(db)
    if not latest:
        return {
            "message": "Aún no hay métricas. Ejecuta /clean y /train.",
            "model_explanation": "Predice demanda a 7 días usando promedio móvil de salidas históricas.",
        }
    return {
        "latest": latest,
        "latest_cleaning": _latest_metrics(db, "cleaning"),
        "latest_training": _latest_metrics(db, "training"),
        "total_metrics": db.model_metrics.count_documents({}),
        "model_explanation": (
            "Predice demanda esperada por medicamento para los próximos días, estima riesgo de agotamiento "
            "y prioriza reposición usando movimientos tipo Exit como demanda histórica."
        ),
    }


@app.get("/health")
def health() -> Dict[str, Any]:
    return _health_response()


@app.post("/seed-test-data")
def seed_test_data(request: IngestRequest = IngestRequest(source="generated")) -> Dict[str, Any]:
    return _seed_test_data(request)


@app.post("/ingest")
def ingest(request: IngestRequest = IngestRequest(source="generated")) -> Dict[str, Any]:
    return _ingest(request)


@app.post("/clean")
def clean() -> Dict[str, Any]:
    return _clean()


@app.post("/train")
def train(request: TrainRequest = TrainRequest()) -> Dict[str, Any]:
    return _train(request)


@app.get("/predictions")
def list_predictions(limit: int = 50) -> List[Dict[str, Any]]:
    return _list_predictions(limit)


@app.get("/predictions/{product_id}")
def get_prediction(product_id: str) -> Dict[str, Any]:
    return _get_prediction(product_id)


@app.get("/metrics")
def metrics() -> Dict[str, Any]:
    return _metrics()


@router.get("/health")
def api_health() -> Dict[str, Any]:
    return _health_response()


@router.post("/seed-test-data")
def api_seed_test_data(
    request: IngestRequest = IngestRequest(source="generated"),
    context: AuthContext = Depends(ADMIN_ONLY),
) -> Dict[str, Any]:
    ensure_dev_seed_enabled(context, ["ADMIN"])
    return _seed_test_data(request)


@router.post("/ingest")
def api_ingest(
    request: IngestRequest = IngestRequest(),
    context: AuthContext = Depends(ADMIN_AUDITOR),
) -> Dict[str, Any]:
    return _ingest(request, context)


@router.post("/clean")
def api_clean(_context: AuthContext = Depends(ADMIN_AUDITOR)) -> Dict[str, Any]:
    return _clean()


@router.post("/train")
def api_train(
    request: TrainRequest = TrainRequest(),
    _context: AuthContext = Depends(ADMIN_AUDITOR),
) -> Dict[str, Any]:
    return _train(request)


@router.post("/recalculate")
def api_recalculate(
    request: TrainRequest = TrainRequest(),
    _context: AuthContext = Depends(ADMIN_AUDITOR),
) -> Dict[str, Any]:
    cleaning_result = _clean()
    training_result = _train(request)
    return {
        "message": "Limpieza y predicción recalculadas.",
        "cleaning": cleaning_result,
        "training": training_result,
    }


@router.get("/metrics")
def api_metrics(_context: AuthContext = Depends(READ_ROLES)) -> Dict[str, Any]:
    return _metrics()


@router.get("")
@router.get("/")
def api_list_predictions(
    limit: int = 50,
    _context: AuthContext = Depends(READ_ROLES),
) -> List[Dict[str, Any]]:
    return _list_predictions(limit)


@router.get("/{product_id}")
def api_get_prediction(
    product_id: str,
    _context: AuthContext = Depends(READ_ROLES),
) -> Dict[str, Any]:
    return _get_prediction(product_id)


app.include_router(router)
