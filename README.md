# FarmaExpres Prediction Service

Microservicio de analítica predictiva para FarmaExpres. Usa **Python + FastAPI** y **MongoDB** para extraer información de inventario desde `inventory-service`, limpiar datos, guardar evidencia analítica y calcular una predicción inicial de demanda y riesgo de agotamiento.

Este repositorio sigue siendo independiente, pero ya no se plantea como una demostración aislada. Su integración oficial es por el ecosistema de FarmaExpres:

```text
Frontend React -> API Gateway -> prediction-service -> inventory-service -> PostgreSQL
                                               |
                                               v
                                            MongoDB
```

## Qué hace

1. Recibe una solicitud desde el frontend principal por `/api/predictions`.
2. El `api-gateway` enruta la solicitud hacia `prediction-service`.
3. `prediction-service` valida JWT y roles.
4. Para sincronizar datos, consulta `inventory-service` por HTTP interno.
5. Guarda datos crudos en MongoDB (`raw_data` y `products_snapshot`).
6. Limpia duplicados, fechas, nombres, cantidades inválidas y registros incompletos.
7. Guarda datos limpios en `cleaned_data`.
8. Calcula demanda esperada a 7 días con promedio móvil de 30 días.
9. Guarda resultados en `predictions` y métricas en `model_metrics`.
10. El frontend principal muestra estado, métricas, prioridad de reposición y tabla de predicciones.

## Stack

- Backend analítico: Python 3.12 + FastAPI.
- Base NoSQL: MongoDB 7.
- Fuente operativa: `inventory-service` del backend FarmaExpres.
- Gateway: Spring Cloud Gateway del backend principal.
- Frontend oficial: React + Vite en `FarmaExpres-Frontend`.
- Frontend local auxiliar: HTML/CSS/JS estático para pruebas rápidas.
- Modelo: promedio móvil de 30 días sobre movimientos `Exit`.

## Colecciones MongoDB

| Colección | Uso |
| --- | --- |
| `raw_data` | Datos crudos recibidos desde `inventory-service` o fuentes locales de prueba. |
| `products_snapshot` | Foto de medicamentos con stock, mínimo, categoría y vencimiento. |
| `cleaned_data` | Datos normalizados y validados para el modelo. |
| `predictions` | Demanda esperada, riesgo y días estimados hasta agotamiento. |
| `model_metrics` | Métricas de limpieza, entrenamiento y error aproximado. |

## Ejecución integrada por ambiente

Cada ambiente se levanta con su archivo `.env` correspondiente. El orden recomendado es:

1. Backend principal.
2. Backend predictivo NoSQL (`mongo` y `prediction-service`).
3. Frontend principal.

Docker Desktop agrupa los contenedores por nombre de proyecto. Por eso este repositorio usa el mismo grupo Docker del backend para que el servicio predictivo quede integrado al ecosistema principal:

| Compose | Contenedores | Grupo esperado en Docker Desktop |
| --- | --- | --- |
| `docker-compose.yml` | `mongo`, `prediction-service` | `farmaexpres-dev`, `farmaexpres-qa` o `farmaexpres-main` |

Con esta organización, el ambiente de desarrollo se ve así:

```text
farmaexpres-dev
  postgres
  auth-service
  inventory-service
  audit-service
  alert-service
  api-gateway
  prediction-service
  mongo

farmaexpres-frontend-dev
  frontend
```

### Desarrollo

```bash
cd ../FarmaExpres_Backend
docker compose --env-file .env.dev up -d --build

cd ../FarmaExpres-Micro-NoSQL
docker compose --env-file .env.dev up -d --build

cd ../FarmaExpres-Frontend/frontend
docker compose --env-file .env.dev up -d --build
```

Puertos por defecto en `dev`:

- Frontend principal: `http://localhost:3000`
- Gateway oficial: `http://localhost:8080`
- Prediction service directo: `http://localhost:8085`
- MongoDB: `mongodb://localhost:27017`

### QA

```bash
cd ../FarmaExpres_Backend
docker compose --env-file .env.qa up -d --build

cd ../FarmaExpres-Micro-NoSQL
docker compose --env-file .env.qa up -d --build

cd ../FarmaExpres-Frontend/frontend
docker compose --env-file .env.qa up -d --build
```

Puertos por defecto en `qa`:

- Frontend principal: `http://localhost:4000`
- Gateway oficial: `http://localhost:9080`
- Prediction service directo: `http://localhost:9085`
- MongoDB: `mongodb://localhost:37017`

### Main

```bash
cd ../FarmaExpres_Backend
docker compose --env-file .env.main up -d --build

cd ../FarmaExpres-Micro-NoSQL
docker compose --env-file .env.main up -d --build

cd ../FarmaExpres-Frontend/frontend
docker compose --env-file .env.main up -d --build
```

Puertos por defecto en `main`:

- Frontend principal: `http://localhost:5000`
- Gateway oficial: `http://localhost:10080`
- Prediction service directo: `http://localhost:10085`
- MongoDB: `mongodb://localhost:47017`

Cada ambiente usa una red Docker diferente:

- `dev`: `BACKEND_NETWORK=farmaexpres-dev_default`
- `qa`: `BACKEND_NETWORK=farmaexpres-qa_default`
- `main`: `BACKEND_NETWORK=farmaexpres-main_default`

Eso permite que `api-gateway` encuentre el contenedor `prediction-service` del mismo ambiente sin mezclar datos ni contenedores.

Las variables de agrupación son:

- `BACKEND_COMPOSE_PROJECT_NAME`: grupo donde quedan `mongo` y `prediction-service`.

> Importante: como el backend principal y el backend predictivo comparten el mismo grupo Docker, evita usar `docker compose down --remove-orphans` desde un solo repositorio.

## Endpoints oficiales por gateway

Todos los endpoints de negocio se consumen por:

```text
http://localhost:8080/api/predictions
```

Puertos del gateway por ambiente:

- `dev`: `http://localhost:8080/api/predictions`
- `qa`: `http://localhost:9080/api/predictions`
- `main`: `http://localhost:10080/api/predictions`

| Método | Ruta | Rol | Descripción |
| --- | --- | --- | --- |
| `GET` | `/api/predictions/health` | público | Revisa estado del microservicio y MongoDB. |
| `POST` | `/api/predictions/ingest` | ADMIN, AUDITOR | Extrae snapshot desde `inventory-service`. |
| `POST` | `/api/predictions/clean` | ADMIN, AUDITOR | Limpia datos crudos en MongoDB. |
| `POST` | `/api/predictions/train` | ADMIN, AUDITOR | Recalcula predicciones. |
| `POST` | `/api/predictions/recalculate` | ADMIN, AUDITOR | Limpia y entrena usando los datos ya cargados. |
| `GET` | `/api/predictions` | ADMIN, AUDITOR, FARMACEUTICO | Lista predicciones. |
| `GET` | `/api/predictions/{productId}` | ADMIN, AUDITOR, FARMACEUTICO | Consulta un medicamento. |
| `GET` | `/api/predictions/metrics` | ADMIN, AUDITOR, FARMACEUTICO | Muestra métricas del modelo. |

## Flujo de prueba con token

1. Inicia sesión en el backend del ambiente correspondiente:

```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"temenico5@gmail.com","password":"admin123"}'
```

2. Usa el token recibido:

```bash
TOKEN="PEGAR_TOKEN_AQUI"

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

## Datos de prueba

Los datos artificiales siguen existiendo para desarrollo local y validación técnica. No representan producción.

```bash
curl -X POST http://localhost:8085/seed-test-data \
  -H "Content-Type: application/json" \
  -d '{"source":"generated","product_count":80,"days":180}'
```

`RELATIONAL_DB_URL` queda como fallback local para análisis técnico, pero la integración oficial del ecosistema usa `inventory-service`.

## Documentación

- [Historias de usuario](docs/HISTORIAS_USUARIO.md)
- [Libro de la base NoSQL](docs/LIBRO_BASE_NOSQL.md)
- [Informe HTML para sustentación](docs/INFORME_PREDICCIONES_NOSQL.html)
- [ABP y alcance](docs/ABP_ALCANCE.md)
- [Arquitectura](docs/ARQUITECTURA.md)
- [Endpoints](docs/ENDPOINTS.md)
- [Modelo predictivo](docs/MODELO_PREDICTIVO.md)
- [Integración local](docs/INTEGRACION_LOCAL.md)
- [MoSCoW](docs/MOSCOW.md)
- [Trazabilidad](docs/TRAZABILIDAD.md)

## Pruebas locales

Validación rápida del núcleo de limpieza y predicción:

```bash
PYTHONPATH=backend python3 -m unittest discover backend/tests
```
