# FarmaExpres Micro NoSQL

Microservicio independiente para analítica predictiva de inventario en FarmaExpres. No reemplaza el backend principal ni modifica sus servicios; toma datos de inventario, los almacena en MongoDB, los limpia y genera una predicción inicial para apoyar decisiones de reposición.

El desarrollo se trabaja en `Develop`, con ramas `QA` y `main` para mantener el mismo orden usado en los repos de backend y frontend.

## Qué hace este módulo

1. Carga datos crudos desde datos simulados o desde PostgreSQL local de `FarmaExpres_Backend`.
2. Guarda esos datos en MongoDB en la colección `raw_data`.
3. Limpia y normaliza campos importantes: nombres, fechas, cantidades, stock, duplicados y registros incompletos.
4. Guarda el resultado en `cleaned_data`.
5. Calcula demanda esperada por medicamento para los próximos 7 días usando promedio móvil de salidas históricas.
6. Marca riesgo de agotamiento según stock actual, stock mínimo y demanda proyectada.
7. Muestra estado, mensajes del proceso, métricas, tabla y gráfica en un frontend pequeño.

Importante: como el backend actual no tiene tabla formal de ventas u órdenes, el modelo usa `motion.type = 'Exit'` como aproximación de demanda. Esto queda documentado para no presentar los resultados como ventas reales.

## Stack

- Backend: Python + FastAPI.
- Base NoSQL: MongoDB.
- Modelo predictivo: promedio móvil de 30 días sobre salidas de inventario.
- Frontend: HTML, CSS y JavaScript estático servido con Nginx.
- Ejecución local: Docker Compose.

## Estructura

```text
backend/      API, ingesta, limpieza, MongoDB y predicción.
frontend/     Tablero simple para estado, métricas, alertas y predicciones.
scripts/      Generación de datos y pipeline local.
docs/         Historias, arquitectura, endpoints, modelo, libro NoSQL, ABP e integración.
docker-compose.yml
.env.dev.example   Plantilla del entorno local dev.
.env.qa.example    Plantilla del entorno local qa.
.env.main.example  Plantilla del entorno local main.
```

## Ejecutar con Docker por entorno

Primero crea el archivo local de entorno que vayas a usar:

```bash
cp .env.dev.example .env.dev
```

Si vas a leer PostgreSQL de `FarmaExpres_Backend`, llena `RELATIONAL_DB_URL` siguiendo el ejemplo comentado en la plantilla y cambia `CHANGE_ME` por la clave local de PostgreSQL. Si solo vas a usar datos simulados, deja `RELATIONAL_DB_URL` vacío.

Dev:

```bash
docker compose --env-file .env.dev up -d --build
```

QA:

```bash
docker compose --env-file .env.qa up -d --build
```

Main local:

```bash
docker compose --env-file .env.main up -d --build
```

En este equipo, si `docker` no aparece en el PATH:

```bash
/Applications/Docker.app/Contents/Resources/bin/docker compose --env-file .env.dev up -d --build
```

Puertos por defecto en dev:

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5174`
- MongoDB: `mongodb://localhost:27017`

## Probar el flujo

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/seed-test-data -H "Content-Type: application/json" -d '{"source":"generated","product_count":80,"days":180}'
curl -X POST http://localhost:8000/clean
curl -X POST http://localhost:8000/train -H "Content-Type: application/json" -d '{"horizon_days":7}'
curl http://localhost:8000/predictions
```

También se puede ejecutar:

```bash
python3 scripts/run_local_pipeline.py --api http://localhost:8000
```

## Integración local con FarmaExpres_Backend

El backend principal se levanta así:

```bash
cd ../FarmaExpres_Backend
docker compose --env-file .env.dev up -d --build
```

En `dev`, PostgreSQL queda publicado en `localhost:5433`. Este microservicio trae una plantilla `.env.dev.example`; el archivo real `.env.dev` se crea localmente y no se sube al repositorio:

```text
RELATIONAL_DB_URL=postgresql://postgres:CHANGE_ME@host.docker.internal:5433/farmaexpres_inventory
```

Luego, desde este repo:

```bash
docker compose --env-file .env.dev up -d --build
curl -X POST http://localhost:8000/ingest -H "Content-Type: application/json" -d '{"source":"postgres"}'
curl -X POST http://localhost:8000/clean
curl -X POST http://localhost:8000/train
```

El backend principal no se modifica. Los scripts de prueba quedan en este repositorio.

## Datos de prueba

El endpoint `POST /seed-test-data` genera por defecto 80 medicamentos y 180 días de movimientos. También se puede generar SQL para la base relacional local:

```bash
python3 scripts/generate_relational_test_data.py --products 100 --days 180
```

Esos datos son artificiales y solo sirven para validar limpieza, carga NoSQL y predicción.

## Documentación

- [Historias de usuario](docs/HISTORIAS_USUARIO.md)
- [Libro de la base NoSQL](docs/LIBRO_BASE_NOSQL.md)
- [ABP y alcance del proyecto](docs/ABP_ALCANCE.md)
- [Arquitectura y análisis del repo principal](docs/ARQUITECTURA.md)
- [Endpoints](docs/ENDPOINTS.md)
- [Modelo predictivo](docs/MODELO_PREDICTIVO.md)
- [Integración local](docs/INTEGRACION_LOCAL.md)
- [MoSCoW y alcance](docs/MOSCOW.md)
- [Trazabilidad](docs/TRAZABILIDAD.md)
