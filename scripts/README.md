# Scripts

Estos scripts son solo para pruebas locales.

## Ejecutar pipeline del microservicio

```bash
python3 scripts/run_local_pipeline.py --api http://localhost:8000
```

Ejecuta estado, carga de datos generados, limpieza, entrenamiento y consulta de predicciones.

## Generar SQL para PostgreSQL relacional

```bash
python3 scripts/generate_relational_test_data.py --products 40 --days 120
```

El archivo queda en `scripts/output/farmaexpres_inventory_test_data.sql`. Se puede ejecutar contra la base `farmaexpres_inventory` del backend principal cuando este corra con Docker. Estos datos no son reales de produccion.
