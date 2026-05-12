# Endpoints

Base local: `http://localhost:8000`

## GET /health

Valida si el backend y MongoDB responden. Tambien devuelve conteos por coleccion.

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

Consulta una prediccion especifica por `product_id`.

## GET /metrics

Muestra metricas de limpieza y entrenamiento.

Campos principales:

- `latest`: ultima metrica registrada.
- `latest_cleaning`: ultima ejecucion de limpieza.
- `latest_training`: ultimo entrenamiento.
- `total_metrics`: cantidad de metricas guardadas.
- `model_explanation`: resumen del uso del modelo.
