from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from pymongo.database import Database

from app.services.sample_data import generate_synthetic_data


def _clear_derived_collections(db: Database) -> None:
    db.cleaned_data.delete_many({})
    db.predictions.delete_many({})


def replace_generated_data(db: Database, product_count: int = 15, days: int = 90) -> Dict[str, Any]:
    raw_records, snapshots = generate_synthetic_data(product_count=product_count, days=days)
    db.raw_data.delete_many({"source": "generated"})
    db.products_snapshot.delete_many({"source": "generated"})
    _clear_derived_collections(db)
    if raw_records:
        db.raw_data.insert_many(raw_records)
    if snapshots:
        db.products_snapshot.insert_many(snapshots)
    return {
        "source": "generated",
        "raw_records_inserted": len(raw_records),
        "products_inserted": len(snapshots),
        "generated_at": datetime.now(timezone.utc),
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

    db.raw_data.delete_many({"source": "postgres"})
    db.products_snapshot.delete_many({"source": "postgres"})
    _clear_derived_collections(db)
    if raw_records:
        db.raw_data.insert_many(raw_records)
    if snapshots:
        db.products_snapshot.insert_many(snapshots)

    return {
        "source": "postgres",
        "raw_records_inserted": len(raw_records),
        "products_inserted": len(snapshots),
        "generated_at": datetime.now(timezone.utc),
    }
