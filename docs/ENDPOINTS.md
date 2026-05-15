# Endpoints

Base local: `http://localhost:8000`

## GET /health

Valida si el backend y MongoDB responden. También devuelve conteos por colección.

## POST /seed-test-data

Carga datos simulados directamente en MongoDB.

Ejemplo:

```json
{
  "source": "generated",
  "product_count": 15,
  "days": 120
}
```

## POST /ingest

Carga datos desde una fuente.

Fuentes:

- `generated`: datos simulados.
- `postgres`: lee `product`, `batch` y `motion` desde PostgreSQL usando `RELATIONAL_DB_URL`.

## POST /clean

Limpia datos en `raw_data` y guarda resultados en `cleaned_data`.

Reglas aplicadas:

- Eliminar duplicados.
- Validar campos nulos.
- Normalizar nombres.
- Convertir fechas.
- Rechazar cantidades negativas.
- Marcar registros incompletos.

## POST /train

Recalcula predicciones.

Ejemplo:

```json
{
  "horizon_days": 7
}
```

## GET /predictions

Lista predicciones ordenadas por demanda esperada.

## GET /predictions/{productId}

Consulta una predicción específica por `product_id`.

## GET /metrics

Muestra métricas de limpieza y entrenamiento.

Campos principales:

- `latest`: última métrica registrada.
- `latest_cleaning`: última ejecución de limpieza.
- `latest_training`: último entrenamiento.
- `total_metrics`: cantidad de métricas guardadas.
- `model_explanation`: resumen del uso del modelo.
