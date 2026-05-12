#!/usr/bin/env python3
"""Generate PostgreSQL test data for FarmaExpres inventory tables."""

import argparse
import random
from datetime import date, datetime, timedelta
from pathlib import Path


NAMES = [
    ("Acetaminofen 500 mg", "ANALGESICO"),
    ("Ibuprofeno 400 mg", "AINE"),
    ("Loratadina 10 mg", "ANTIALERGICO"),
    ("Amoxicilina 500 mg", "ANTIBIOTICO"),
    ("Omeprazol 20 mg", "GASTRO"),
    ("Metformina 850 mg", "CRONICO"),
    ("Losartan 50 mg", "CRONICO"),
    ("Salbutamol inhalador", "RESPIRATORIO"),
]


def sql_text(product_count, days, seed):
    rng = random.Random(seed)
    today = date.today()
    lines = [
        "-- Test data for local development only.",
        "-- Execute against database farmaexpres_inventory.",
        "BEGIN;",
    ]

    for index in range(1, product_count + 1):
        base_name, group = rng.choice(NAMES)
        code = f"FXT-{index:04d}"
        stock = rng.randint(25, 220)
        minimum = rng.randint(8, 30)
        unit_price = rng.randint(20, 210) * 100
        expiration = today + timedelta(days=rng.randint(60, 450))
        product_name = f"{base_name} Test {index}"
        lines.append(
            "INSERT INTO product (name, nombre_generico, concentracion, forma_farmaceutica, "
            "presentacion, code, stock, unitprice, stock_maximo, precio_compra, precio_venta, "
            "requiere_receta, laboratorio, registro_sanitario, via_administracion, unidad_medida, "
            "ubicacion_almacen, temperatura_conservacion, observaciones, asset, minimumstock, expirationdate) "
            f"VALUES ('{product_name}', '{base_name}', 'NA', 'OTRO', 'Prueba local', "
            f"'{code}', {stock}, {unit_price}, {stock + 120}, {unit_price * 0.55:.2f}, {unit_price}, "
            f"FALSE, 'LAB TEST', 'RS-{code}', 'ORAL', 'CAJA', 'Bodega prueba', 'AMBIENTE', "
            "'Datos generados para prediccion local', TRUE, {minimum}, '{expiration}') "
            "ON CONFLICT (code) DO NOTHING;"
        )
        lines.append(
            "INSERT INTO batch (product_id, batch_code, expiration_date, initial_stock, available_stock, status) "
            f"SELECT id, 'TEST-{code}', expirationdate, stock, stock, 'ACTIVE' FROM product WHERE code = '{code}' "
            "ON CONFLICT (product_id, batch_code) DO NOTHING;"
        )

        for day_offset in range(days):
            movement_day = datetime.combine(today - timedelta(days=days - day_offset), datetime.min.time())
            demand = max(0, int(rng.gauss(5 + (index % 4), 2)))
            if demand == 0:
                continue
            lines.append(
                "INSERT INTO motion (type, amount, date_time, reason, user_name, user_email, user_role, "
                "status, produc_id, batch_id) "
                f"SELECT 'Exit', {demand}, '{movement_day.isoformat()}', 'Venta simulada para pruebas NoSQL', "
                "'SCRIPT_TEST', 'script@farmaexpres.local', 'SYSTEM', 'NORMAL', p.id, b.id "
                "FROM product p JOIN batch b ON b.product_id = p.id "
                f"WHERE p.code = '{code}' AND b.batch_code = 'TEST-{code}';"
            )

    lines.append("COMMIT;")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate FarmaExpres inventory SQL test data.")
    parser.add_argument("--products", type=int, default=40)
    parser.add_argument("--days", type=int, default=120)
    parser.add_argument("--seed", type=int, default=271)
    parser.add_argument("--output", default="scripts/output/farmaexpres_inventory_test_data.sql")
    args = parser.parse_args()

    content = sql_text(args.products, args.days, args.seed)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    print(f"Generated {output} with {args.products} products and {args.days} days.")


if __name__ == "__main__":
    main()
