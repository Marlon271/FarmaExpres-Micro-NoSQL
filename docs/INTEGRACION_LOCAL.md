# Integración local con FarmaExpres

## Objetivo

Ejecutar `prediction-service` como parte del ecosistema FarmaExpres, consumiendo datos desde `inventory-service` y exponiendo resultados por el `api-gateway`.

## Flujo oficial

```mermaid
flowchart LR
    A["Frontend React"] --> B["API Gateway"]
    B --> C["prediction-service"]
    C --> D["inventory-service"]
    D --> E["PostgreSQL inventory"]
    C --> F["MongoDB predictions"]
```

MongoDB no consulta PostgreSQL directamente. La extracción la hace Python por HTTP interno hacia `inventory-service`.

## 1. Levantar backend principal

```bash
cd ../FarmaExpres_Backend
docker compose --env-file .env.dev up -d --build
```

Servicios esperados:

- `api-gateway`: `http://localhost:8080`
- `inventory-service`: interno `http://inventory-service:8082`
- PostgreSQL: `localhost:5433`

## 2. Levantar prediction-service

```bash
cd ../FarmaExpres-Micro-NoSQL
cp .env.dev.example .env.dev
docker compose --env-file .env.dev up -d --build
```

La variable clave es:

```text
BACKEND_NETWORK=farmaexpres-dev_default
```

Con esa red, el gateway del backend puede resolver:

```text
http://prediction-service:8000
```

## 3. Probar por gateway

Primero obtener token:

```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"temenico5@gmail.com","password":"admin123"}'
```

Luego ejecutar:

```bash
TOKEN="PEGAR_TOKEN_AQUI"

curl http://localhost:8080/api/predictions/health

curl -X POST http://localhost:8080/api/predictions/ingest \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"source":"inventory"}'

curl -X POST http://localhost:8080/api/predictions/clean \
  -H "Authorization: Bearer $TOKEN"

curl -X POST http://localhost:8080/api/predictions/train \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"horizon_days":7}'

curl http://localhost:8080/api/predictions \
  -H "Authorization: Bearer $TOKEN"
```

## 4. Frontend principal

El frontend integrado consume el gateway con rutas relativas:

```text
/api/predictions
```

El módulo visual queda dentro de `FarmaExpres-Frontend`, no como una aplicación separada para usuarios finales.

## 5. Herramientas locales de apoyo

El frontend estático de este repositorio se conserva como tablero auxiliar de diagnóstico:

```text
http://localhost:5174
```

Los datos generados por `POST /seed-test-data` y el fallback `RELATIONAL_DB_URL` son solo para pruebas técnicas. La integración oficial usa `inventory-service`.
