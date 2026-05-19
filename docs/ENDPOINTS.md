# Endpoints

La integración oficial se consume por el gateway del backend principal:

```text
http://localhost:8080/api/predictions
```

El puerto directo del microservicio (`http://localhost:8085`) queda para diagnóstico local.

## GET /api/predictions/health

Valida si FastAPI y MongoDB responden. Devuelve conteos por colección y estado del flujo.

## POST /api/predictions/ingest

Extrae datos desde `inventory-service` usando el token JWT recibido desde el frontend.

Body recomendado:

```json
{
  "source": "inventory"
}
```

Roles permitidos:

- `ADMIN`
- `AUDITOR`

## POST /api/predictions/clean

Limpia datos en `raw_data` y guarda el resultado en `cleaned_data`.

Reglas aplicadas:

- eliminar duplicados;
- validar campos nulos;
- normalizar nombres;
- convertir fechas;
- detectar cantidades negativas;
- marcar registros incompletos.

Roles permitidos:

- `ADMIN`
- `AUDITOR`

## POST /api/predictions/train

Recalcula predicciones con promedio móvil.

Ejemplo:

```json
{
  "horizon_days": 7
}
```

Roles permitidos:

- `ADMIN`
- `AUDITOR`

## POST /api/predictions/recalculate

Ejecuta limpieza y entrenamiento sobre los datos que ya están cargados en MongoDB.

Roles permitidos:

- `ADMIN`
- `AUDITOR`

## GET /api/predictions

Lista predicciones ordenadas por demanda esperada y riesgo.

Roles permitidos:

- `ADMIN`
- `AUDITOR`
- `FARMACEUTICO`

## GET /api/predictions/{productId}

Consulta la predicción de un medicamento específico por `product_id`.

## GET /api/predictions/metrics

Muestra métricas de limpieza y entrenamiento.

Campos principales:

- `latest`: última métrica registrada.
- `latest_cleaning`: última ejecución de limpieza.
- `latest_training`: último entrenamiento.
- `total_metrics`: cantidad de métricas guardadas.
- `model_explanation`: explicación corta del modelo.

## Endpoints locales de apoyo

Estos endpoints existen para desarrollo directo contra `prediction-service`:

- `GET /health`
- `POST /seed-test-data`
- `POST /ingest`
- `POST /clean`
- `POST /train`
- `GET /predictions`
- `GET /metrics`

`POST /seed-test-data` solo debe usarse para pruebas técnicas; no representa datos reales.
