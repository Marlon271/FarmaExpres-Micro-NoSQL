from __future__ import annotations

import random
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple


PRODUCT_NAMES = [
    ("ACM-001", "Acetaminophen 500mg", "Analgesicos"),
    ("IBU-001", "Ibuprofen 400mg", "Antiinflamatorios"),
    ("LOT-001", "Loratadina 10 mg", "Antialergicos"),
    ("AMX-001", "Amoxicillin 500mg", "Antibioticos"),
    ("OMP-001", "Omeprazol 20 mg", "Gastrointestinal"),
    ("DCF-001", "Diclofenaco 50 mg", "Antiinflamatorios"),
    ("VIC-001", "Vitamina C 1 g", "Vitaminas"),
    ("SAT-001", "Salbutamol Inhalador", "Respiratorio"),
    ("MET-001", "Metformina 850 mg", "Cronicos"),
    ("SIM-001", "Simvastatina 20 mg", "Cronicos"),
    ("LOS-001", "Losartan 50 mg", "Cronicos"),
    ("INS-001", "Insulina NPH", "Cronicos"),
    ("AZT-001", "Azitromicina 500 mg", "Antibioticos"),
    ("CTZ-001", "Cetirizina 10 mg", "Antialergicos"),
    ("NPR-001", "Naproxeno 250 mg", "Antiinflamatorios"),
]


def _random_price(rng: random.Random) -> float:
    return float(rng.randint(18, 180) * 100)


def generate_synthetic_data(
    product_count: int = 15,
    days: int = 90,
    seed: int = 271,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    rng = random.Random(seed)
    today = date.today()
    selected = PRODUCT_NAMES[: max(1, min(product_count, len(PRODUCT_NAMES)))]
    raw_records: List[Dict[str, Any]] = []
    snapshots: List[Dict[str, Any]] = []

    for index, (code, name, category) in enumerate(selected, start=1):
        base_demand = rng.randint(1, 9)
        current_stock = rng.randint(8, 180)
        minimum_stock = rng.randint(8, 25)
        max_stock = max(current_stock + rng.randint(60, 180), minimum_stock + 40)
        expiration = today + timedelta(days=rng.randint(45, 420))
        batch_code = f"TEST-{code}-{today:%Y%m}"
        product_id = str(index)

        snapshots.append(
            {
                "product_id": product_id,
                "product_code": code,
                "product_name": name,
                "category": category,
                "current_stock": current_stock,
                "minimum_stock": minimum_stock,
                "stock_maximo": max_stock,
                "unit_price": _random_price(rng),
                "expiration_date": expiration.isoformat(),
                "source": "generated",
                "generated_at": datetime.now(timezone.utc),
            }
        )

        for day_offset in range(days):
            movement_day = today - timedelta(days=days - day_offset)
            seasonal_boost = 2 if movement_day.weekday() in (0, 4, 5) else 0
            demand = max(0, int(rng.gauss(base_demand + seasonal_boost, 2)))
            if rng.random() < 0.08:
                demand += rng.randint(5, 14)

            if demand > 0:
                raw_records.append(
                    {
                        "source": "generated",
                        "product_id": product_id,
                        "product_code": code,
                        "product_name": name,
                        "category": category,
                        "movement_type": "Exit",
                        "amount": demand,
                        "movement_date": movement_day.isoformat(),
                        "stock": max(current_stock - demand, 0),
                        "minimum_stock": minimum_stock,
                        "unit_price": _random_price(rng),
                        "batch_code": batch_code,
                        "expiration_date": expiration.isoformat(),
                        "user_role": rng.choice(["ADMIN", "FARMACEUTICO", "SYSTEM"]),
                    }
                )

            if rng.random() < 0.12:
                entrance_amount = rng.randint(10, 55)
                raw_records.append(
                    {
                        "source": "generated",
                        "product_id": product_id,
                        "product_code": code,
                        "product_name": name,
                        "category": category,
                        "movement_type": "Entrance",
                        "amount": entrance_amount,
                        "movement_date": movement_day.isoformat(),
                        "stock": min(current_stock + entrance_amount, max_stock),
                        "minimum_stock": minimum_stock,
                        "unit_price": _random_price(rng),
                        "batch_code": batch_code,
                        "expiration_date": expiration.isoformat(),
                        "user_role": "SYSTEM",
                    }
                )

        # A few controlled dirty rows make the cleaning process visible.
        if raw_records:
            raw_records.append(dict(raw_records[-1]))
            raw_records.append(
                {
                    "source": "generated",
                    "product_id": product_id,
                    "product_code": code,
                    "product_name": "   " + name.lower() + "   ",
                    "category": category,
                    "movement_type": "Exit",
                    "amount": -3,
                    "movement_date": today.isoformat(),
                    "stock": current_stock,
                    "minimum_stock": minimum_stock,
                    "batch_code": batch_code,
                    "expiration_date": expiration.isoformat(),
                }
            )

    return raw_records, snapshots
