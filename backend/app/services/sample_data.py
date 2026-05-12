from __future__ import annotations

import random
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple


PRODUCT_TEMPLATES = [
    ("Acetaminofen", "500 mg", "TABLETA", "Analgesicos"),
    ("Ibuprofeno", "400 mg", "TABLETA", "Antiinflamatorios"),
    ("Loratadina", "10 mg", "TABLETA", "Antialergicos"),
    ("Amoxicilina", "500 mg", "CAPSULA", "Antibioticos"),
    ("Omeprazol", "20 mg", "CAPSULA", "Gastrointestinal"),
    ("Diclofenaco", "50 mg", "TABLETA", "Antiinflamatorios"),
    ("Vitamina C", "1 g", "TABLETA", "Vitaminas"),
    ("Salbutamol", "100 mcg", "INHALADOR", "Respiratorio"),
    ("Metformina", "850 mg", "TABLETA", "Cronicos"),
    ("Simvastatina", "20 mg", "TABLETA", "Cronicos"),
    ("Losartan", "50 mg", "TABLETA", "Cronicos"),
    ("Insulina NPH", "100 UI", "VIAL", "Cronicos"),
    ("Azitromicina", "500 mg", "TABLETA", "Antibioticos"),
    ("Cetirizina", "10 mg", "TABLETA", "Antialergicos"),
    ("Naproxeno", "250 mg", "TABLETA", "Antiinflamatorios"),
    ("Clotrimazol", "1%", "CREMA", "Dermatologicos"),
    ("Enalapril", "20 mg", "TABLETA", "Cronicos"),
    ("Hidroclorotiazida", "25 mg", "TABLETA", "Cronicos"),
    ("Fluconazol", "150 mg", "CAPSULA", "Antimicoticos"),
    ("Prednisolona", "5 mg", "TABLETA", "Corticoides"),
    ("Dexametasona", "4 mg", "AMPOLLA", "Corticoides"),
    ("Suero oral", "60 mEq", "SOBRE", "Hidratacion"),
    ("Alcohol antiseptico", "70%", "FRASCO", "Aseo"),
    ("Acido folico", "1 mg", "TABLETA", "Vitaminas"),
    ("Sulfato ferroso", "300 mg", "TABLETA", "Suplementos"),
]


def _random_price(rng: random.Random) -> float:
    return float(rng.randint(18, 180) * 100)


def generate_synthetic_data(
    product_count: int = 80,
    days: int = 180,
    seed: int = 271,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    rng = random.Random(seed)
    today = date.today()
    selected = []
    for index in range(1, max(1, product_count) + 1):
        base_name, strength, dosage_form, category = PRODUCT_TEMPLATES[(index - 1) % len(PRODUCT_TEMPLATES)]
        cycle = (index - 1) // len(PRODUCT_TEMPLATES)
        suffix = "" if cycle == 0 else f" L{cycle + 1}"
        code = f"FXN-{index:04d}"
        selected.append((code, f"{base_name} {strength}{suffix}", dosage_form, category))
    raw_records: List[Dict[str, Any]] = []
    snapshots: List[Dict[str, Any]] = []

    for index, (code, name, dosage_form, category) in enumerate(selected, start=1):
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
                "forma_farmaceutica": dosage_form,
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
                        "forma_farmaceutica": dosage_form,
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
                        "forma_farmaceutica": dosage_form,
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
