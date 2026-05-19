from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

ALLOWED_MOVEMENTS = {"Entrance", "Exit", "Updated", "Deleted", "Snapshot"}


def normalize_name(value: Any) -> str:
    text = "" if value is None else str(value).strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"\s+", " ", text)
    return text.upper()


def parse_date(value: Any) -> Optional[str]:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        clean = value.strip()
        clean = clean[:-1] + "+00:00" if clean.endswith("Z") else clean
        clean = re.sub(r"(\.\d{6})\d+([+-]\d{2}:?\d{2})?$", r"\1\2", clean)
        try:
            return datetime.fromisoformat(clean).isoformat()
        except ValueError:
            try:
                return date.fromisoformat(clean[:10]).isoformat()
            except ValueError:
                return None
    return None


def _as_int(value: Any) -> int | None:
    try:
        if value is None or value == "":
            return None
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _as_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def clean_records(raw_records: Iterable[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    records = list(raw_records)
    cleaned: List[Dict[str, Any]] = []
    seen = set()
    duplicates_removed = 0
    invalid_records = 0

    for record in records:
        amount = _as_int(record.get("amount", record.get("quantity")))
        stock = _as_int(record.get("stock", record.get("current_stock")))
        minimum_stock = _as_int(record.get("minimum_stock", record.get("minimumstock")))
        movement_date = parse_date(record.get("movement_date", record.get("date_time")))
        expiration_date = parse_date(record.get("expiration_date", record.get("expirationdate")))
        movement_type = str(record.get("movement_type", record.get("type", "Snapshot"))).strip()
        if movement_type not in ALLOWED_MOVEMENTS:
            movement_type = "Snapshot"

        product_id = record.get("product_id") or record.get("id") or record.get("produc_id")
        product_code = str(record.get("product_code", record.get("code", ""))).strip()
        product_name_raw = record.get("product_name", record.get("name"))
        normalized_name = normalize_name(product_name_raw)

        flags = []
        if not product_id and not product_code:
            flags.append("missing_product_identifier")
        if not normalized_name:
            flags.append("missing_product_name")
        if amount is None:
            flags.append("missing_amount")
        elif amount < 0:
            flags.append("negative_amount")
        if stock is None:
            flags.append("missing_stock")
        elif stock < 0:
            flags.append("negative_stock")
        if movement_date is None:
            flags.append("invalid_movement_date")
        if minimum_stock is not None and minimum_stock < 0:
            flags.append("negative_minimum_stock")

        duplicate_key = (
            str(product_id or product_code),
            movement_type,
            movement_date,
            amount,
            str(record.get("batch_code", "")),
        )
        if duplicate_key in seen:
            duplicates_removed += 1
            continue
        seen.add(duplicate_key)

        is_valid = not flags
        if not is_valid:
            invalid_records += 1

        cleaned.append(
            {
                "source": record.get("source", "unknown"),
                "source_record_id": str(record.get("movement_id", record.get("_id", ""))),
                "product_id": str(product_id or product_code),
                "product_code": product_code,
                "product_name": str(product_name_raw or "").strip(),
                "normalized_product_name": normalized_name,
                "category": str(record.get("category", record.get("forma_farmaceutica", ""))).strip(),
                "movement_type": movement_type,
                "amount": amount if amount is not None else 0,
                "movement_date": movement_date,
                "stock": stock if stock is not None else 0,
                "minimum_stock": minimum_stock if minimum_stock is not None else 0,
                "unit_price": _as_float(record.get("unit_price", record.get("precio_venta", record.get("unitprice")))),
                "batch_code": str(record.get("batch_code", "")).strip(),
                "expiration_date": expiration_date,
                "user_role": str(record.get("user_role", "")).strip(),
                "is_valid": is_valid,
                "quality_flags": flags,
                "cleaned_at": datetime.now(timezone.utc),
            }
        )

    metrics = {
        "input_records": len(records),
        "cleaned_records": len(cleaned),
        "valid_records": len([item for item in cleaned if item["is_valid"]]),
        "invalid_records": invalid_records,
        "duplicates_removed": duplicates_removed,
    }
    return cleaned, metrics
