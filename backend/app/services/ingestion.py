from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from pymongo import ReplaceOne
from pymongo.database import Database

from app.services.sample_data import generate_synthetic_data


def _clear_derived_collections(db: Database) -> None:
    db.cleaned_data.delete_many({})
    db.predictions.delete_many({})


def _replace_products_snapshot(db: Database, snapshots: List[Dict[str, Any]]) -> int:
    operations = []
    for snapshot in snapshots:
        product_id = str(snapshot.get("product_id") or snapshot.get("product_code") or "").strip()
        if not product_id:
            continue
        normalized_snapshot = dict(snapshot, product_id=product_id)
        operations.append(
            ReplaceOne(
                {"product_id": product_id},
                normalized_snapshot,
                upsert=True,
            )
        )

    if operations:
        db.products_snapshot.bulk_write(operations, ordered=False)
    return len(operations)


def _replace_active_training_dataset(
    db: Database,
    raw_records: List[Dict[str, Any]],
    snapshots: List[Dict[str, Any]],
) -> int:
    db.raw_data.delete_many({})
    db.products_snapshot.delete_many({})
    _clear_derived_collections(db)
    if raw_records:
        db.raw_data.insert_many(raw_records)
    return _replace_products_snapshot(db, snapshots)


def replace_generated_data(db: Database, product_count: int = 80, days: int = 180) -> Dict[str, Any]:
    raw_records, snapshots = generate_synthetic_data(product_count=product_count, days=days)
    products_loaded = _replace_active_training_dataset(db, raw_records, snapshots)
    return {
        "source": "generated",
        "raw_records_inserted": len(raw_records),
        "products_inserted": products_loaded,
        "generated_at": datetime.now(timezone.utc),
    }


def ingest_from_inventory_snapshot(db: Database, snapshot: Dict[str, Any]) -> Dict[str, Any]:
    products = snapshot.get("products") or []
    batches = snapshot.get("batches") or []
    movements = snapshot.get("movements") or []
    generated_at = datetime.now(timezone.utc)

    products_by_id = {str(product.get("productId")): product for product in products if product.get("productId")}
    batches_by_id = {str(batch.get("batchId")): batch for batch in batches if batch.get("batchId")}

    snapshots: List[Dict[str, Any]] = []
    raw_records: List[Dict[str, Any]] = []

    for product in products:
        product_id = str(product.get("productId") or product.get("productCode") or "")
        if not product_id:
            continue
        snapshots.append(
            {
                "source": "inventory-service",
                "product_id": product_id,
                "product_code": product.get("productCode", ""),
                "product_name": product.get("productName", ""),
                "generic_name": product.get("genericName", ""),
                "category": product.get("category") or product.get("dosageForm") or "",
                "current_stock": product.get("currentStock", 0),
                "minimum_stock": product.get("minimumStock", 0),
                "stock_maximo": product.get("maximumStock"),
                "unit_price": product.get("unitPrice"),
                "precio_venta": product.get("salePrice"),
                "expiration_date": product.get("expirationDate"),
                "active": product.get("active", True),
                "generated_at": generated_at,
            }
        )

    for movement in movements:
        product_id = str(movement.get("productId") or "")
        product = products_by_id.get(product_id, {})
        batch = batches_by_id.get(str(movement.get("batchId") or ""), {})
        raw_records.append(
            {
                "source": "inventory-service",
                "product_id": product_id,
                "product_code": movement.get("productCode") or product.get("productCode", ""),
                "product_name": movement.get("productName") or product.get("productName", ""),
                "category": product.get("category") or product.get("dosageForm") or "",
                "movement_id": movement.get("movementId"),
                "movement_type": movement.get("movementType", "Snapshot"),
                "amount": movement.get("amount", 0),
                "movement_date": movement.get("movementDate"),
                "stock": movement.get("stock", product.get("currentStock", 0)),
                "minimum_stock": movement.get("minimumStock", product.get("minimumStock", 0)),
                "batch_id": movement.get("batchId"),
                "batch_code": movement.get("batchCode") or batch.get("batchCode", ""),
                "expiration_date": movement.get("expirationDate") or product.get("expirationDate"),
                "batch_expiration_date": movement.get("batchExpirationDate") or batch.get("expirationDate"),
                "user_id": movement.get("userId"),
                "user_name": movement.get("userName", ""),
                "user_email": movement.get("userEmail", ""),
                "user_role": movement.get("userRole", ""),
            }
        )

    if not raw_records:
        raw_records = [
            {
                "source": "inventory-service",
                "product_id": item["product_id"],
                "product_code": item.get("product_code", ""),
                "product_name": item.get("product_name", ""),
                "category": item.get("category", ""),
                "movement_type": "Snapshot",
                "amount": 0,
                "movement_date": generated_at,
                "stock": item.get("current_stock", 0),
                "minimum_stock": item.get("minimum_stock", 0),
                "expiration_date": item.get("expiration_date"),
            }
            for item in snapshots
        ]

    products_loaded = _replace_active_training_dataset(db, raw_records, snapshots)

    return {
        "source": "inventory-service",
        "raw_records_inserted": len(raw_records),
        "products_inserted": products_loaded,
        "movements_received": len(movements),
        "batches_received": len(batches),
        "generated_at": generated_at,
    }


def ingest_from_postgres(db: Database, relational_db_url: str) -> Dict[str, Any]:
    if not relational_db_url:
        return replace_generated_data(db)

    import psycopg2
    from psycopg2.extras import RealDictCursor

    query = """
        SELECT
            p.id AS product_id,
            p.code AS product_code,
            p.name AS product_name,
            p.nombre_generico,
            p.forma_farmaceutica AS category,
            p.stock,
            p.minimumstock AS minimum_stock,
            p.stock_maximo,
            p.unitprice,
            p.precio_venta,
            p.expirationdate AS expiration_date,
            b.id AS batch_id,
            b.batch_code,
            b.available_stock,
            b.expiration_date AS batch_expiration_date,
            m.id AS movement_id,
            COALESCE(m.type, 'Snapshot') AS movement_type,
            COALESCE(m.amount, 0) AS amount,
            COALESCE(m.date_time, NOW()) AS movement_date,
            m.reason,
            m.user_role
        FROM product p
        LEFT JOIN batch b
            ON b.product_id = p.id
        LEFT JOIN motion m
            ON m.produc_id = p.id
           AND (m.batch_id = b.id OR m.batch_id IS NULL)
        ORDER BY p.id, m.date_time;
    """

    snapshot_query = """
        SELECT
            id AS product_id,
            code AS product_code,
            name AS product_name,
            forma_farmaceutica AS category,
            stock AS current_stock,
            minimumstock AS minimum_stock,
            stock_maximo,
            unitprice,
            precio_venta,
            expirationdate AS expiration_date
        FROM product
        ORDER BY id;
    """

    with psycopg2.connect(relational_db_url) as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query)
            raw_records: List[Dict[str, Any]] = [dict(row, source="postgres") for row in cursor.fetchall()]
            cursor.execute(snapshot_query)
            snapshots: List[Dict[str, Any]] = [
                dict(row, source="postgres", generated_at=datetime.now(timezone.utc))
                for row in cursor.fetchall()
            ]

    products_loaded = _replace_active_training_dataset(db, raw_records, snapshots)

    return {
        "source": "postgres",
        "raw_records_inserted": len(raw_records),
        "products_inserted": products_loaded,
        "generated_at": datetime.now(timezone.utc),
    }
