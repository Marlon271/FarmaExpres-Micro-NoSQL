from __future__ import annotations

import math
from collections import defaultdict
from datetime import date, datetime, timezone
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional, Tuple


def _to_date(value: Any) -> Optional[date]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(str(value)[:10])
        except ValueError:
            return None


def _risk_level(stock: int, minimum_stock: int, predicted_units: int, daily_average: float) -> str:
    if stock <= 0:
        return "OUT_OF_STOCK"
    if daily_average > 0 and stock <= predicted_units:
        return "HIGH"
    if stock <= minimum_stock:
        return "MEDIUM"
    return "LOW"


def _calculate_mae(daily_amounts: Dict[date, int]) -> float | None:
    ordered_days = sorted(daily_amounts)
    errors = []
    for index in range(7, len(ordered_days)):
        previous_days = ordered_days[index - 7 : index]
        prediction = mean(daily_amounts[day] for day in previous_days)
        actual = daily_amounts[ordered_days[index]]
        errors.append(abs(actual - prediction))
    if not errors:
        return None
    return round(mean(errors), 2)


def build_predictions(
    cleaned_records: Iterable[Dict[str, Any]],
    snapshots: Iterable[Dict[str, Any]],
    horizon_days: int = 7,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    products: Dict[str, Dict[str, Any]] = {}
    exits_by_product: Dict[str, Dict[date, int]] = defaultdict(lambda: defaultdict(int))
    valid_records = 0

    for snapshot in snapshots:
        product_id = str(snapshot.get("product_id") or snapshot.get("product_code"))
        if product_id:
            products[product_id] = {
                "product_id": product_id,
                "product_code": snapshot.get("product_code", ""),
                "product_name": snapshot.get("product_name", ""),
                "category": snapshot.get("category", ""),
                "stock": int(snapshot.get("current_stock", snapshot.get("stock", 0)) or 0),
                "minimum_stock": int(snapshot.get("minimum_stock", 0) or 0),
            }

    for record in cleaned_records:
        if not record.get("is_valid", False):
            continue
        valid_records += 1
        product_id = str(record.get("product_id"))
        products.setdefault(
            product_id,
            {
                "product_id": product_id,
                "product_code": record.get("product_code", ""),
                "product_name": record.get("product_name", ""),
                "category": record.get("category", ""),
                "stock": int(record.get("stock", 0) or 0),
                "minimum_stock": int(record.get("minimum_stock", 0) or 0),
            },
        )
        products[product_id]["stock"] = int(record.get("stock", products[product_id]["stock"]) or 0)
        products[product_id]["minimum_stock"] = int(
            record.get("minimum_stock", products[product_id]["minimum_stock"]) or 0
        )
        if record.get("movement_type") == "Exit":
            movement_day = _to_date(record.get("movement_date"))
            if movement_day:
                exits_by_product[product_id][movement_day] += int(record.get("amount", 0) or 0)

    generated_at = datetime.now(timezone.utc)
    predictions: List[Dict[str, Any]] = []
    mae_values: List[float] = []

    for product_id, product in products.items():
        daily_amounts = exits_by_product.get(product_id, {})
        ordered_days = sorted(daily_amounts)
        last_day = ordered_days[-1] if ordered_days else date.today()
        window_start = last_day.toordinal() - 29
        recent_total = sum(
            amount for day, amount in daily_amounts.items() if day.toordinal() >= window_start
        )
        moving_average_daily = round(recent_total / 30, 2)
        predicted_units = int(math.ceil(moving_average_daily * horizon_days))
        stock = int(product.get("stock", 0) or 0)
        minimum_stock = int(product.get("minimum_stock", 0) or 0)
        stockout_days = round(stock / moving_average_daily, 1) if moving_average_daily > 0 else None
        mae = _calculate_mae(daily_amounts)
        if mae is not None:
            mae_values.append(mae)

        predictions.append(
            {
                "product_id": product_id,
                "product_code": product.get("product_code", ""),
                "product_name": product.get("product_name", ""),
                "category": product.get("category", ""),
                "current_stock": stock,
                "minimum_stock": minimum_stock,
                "horizon_days": horizon_days,
                "moving_average_daily": moving_average_daily,
                "predicted_demand_units": predicted_units,
                "estimated_stockout_days": stockout_days,
                "risk_level": _risk_level(stock, minimum_stock, predicted_units, moving_average_daily),
                "demand_signal": recent_total,
                "method": "30_day_moving_average",
                "generated_at": generated_at,
            }
        )

    risk_order = {"OUT_OF_STOCK": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    predictions.sort(
        key=lambda item: (
            risk_order.get(item["risk_level"], 4),
            -item["predicted_demand_units"],
        )
    )
    metrics = {
        "trained_at": generated_at,
        "method": "30_day_moving_average",
        "horizon_days": horizon_days,
        "products_evaluated": len(predictions),
        "valid_records_used": valid_records,
        "average_mae": round(mean(mae_values), 2) if mae_values else None,
        "risk_high_count": len([item for item in predictions if item["risk_level"] == "HIGH"]),
        "risk_out_of_stock_count": len([item for item in predictions if item["risk_level"] == "OUT_OF_STOCK"]),
    }
    return predictions, metrics
