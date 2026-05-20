# Trazabilidad del servicio predictivo NoSQL

Este documento conecta los objetivos solicitados con los entregables implementados para integrar `prediction-service` al ecosistema FarmaExpres.

## Resumen

El servicio predictivo queda como microservicio analítico de FarmaExpres para:

- almacenar datos procesados en MongoDB;
- extraer información desde `inventory-service`;
- limpiar datos crudos;
- generar datos de prueba solo para validación local;
- calcular demanda aproximada con promedio móvil;
- visualizar resultados en el frontend principal;
- documentar ejecución, endpoints, historias y alcance.

La integración oficial ya no consulta tablas relacionales de forma directa. PostgreSQL sigue siendo fuente operativa, `inventory-service` mantiene la propiedad del inventario y `prediction-service` consume un contrato HTTP interno.

## Trazabilidad por objetivo

| Objetivo | Implementación | Evidencia |
| --- | --- | --- |
| Crear base no relacional | MongoDB en Docker Compose con volumen persistente | `docker-compose.yml`, `backend/app/database.py` |
| Diseñar colecciones NoSQL | `raw_data`, `cleaned_data`, `predictions`, `model_metrics`, `products_snapshot` | `backend/app/database.py` |
| Extraer datos del sistema relacional | Snapshot HTTP desde `inventory-service` | `POST /api/predictions/ingest`, `backend/app/services/inventory_client.py` |
| Respetar arquitectura de microservicios | Gateway enruta `/api/predictions/**` y Python no lee el esquema de inventario como flujo oficial | Backend `api-gateway`, `inventory-service` |
| Generar datos de prueba | Datos sintéticos locales y script SQL auxiliar | `POST /seed-test-data`, `scripts/generate_relational_test_data.py` |
| Limpiar datos | Normalización, validación, duplicados y banderas de calidad | `POST /api/predictions/clean`, `backend/app/services/cleaning.py` |
| Crear modelo predictivo inicial | Promedio móvil de 30 días sobre salidas de inventario | `POST /api/predictions/train`, `backend/app/services/prediction.py` |
| Visualizar resultados | Módulo `Predicciones` dentro del portal React principal | `FarmaExpres-Frontend/frontend/src/predictions` |
| Documentar historias | Historias base y tres historias MDRT de integración | `docs/HISTORIAS_USUARIO.md`, `docs/historias/*.md` |
| Documentar endpoints | Rutas oficiales por gateway y rutas locales de apoyo | `docs/ENDPOINTS.md` |
| Documentar modelo | Explicación del método, riesgo y limitaciones | `docs/MODELO_PREDICTIVO.md` |
| Documentar integración | Ejecución con backend, gateway, red Docker y MongoDB | `docs/INTEGRACION_LOCAL.md`, `README.md` |
| Documentar alcance | MoSCoW: hecho, pendiente y no incluido | `docs/MOSCOW.md` |
| Explicar metodología NoSQL | Libro con modelado, extracción, limpieza, algoritmo y diagramas | `docs/LIBRO_BASE_NOSQL.md` |
| Documentar ABP | Problema, pregunta guía, alcance, metodología y entregables | `docs/ABP_ALCANCE.md` |

## Trazabilidad por historia de usuario

| Historia | Entregable principal | Estado |
| --- | --- | --- |
| HU-01 Base de datos NoSQL | MongoDB + colecciones + health check | Completa |
| HU-02 Importar datos relacionales | Fallback local por `RELATIONAL_DB_URL` | Conservada para pruebas |
| HU-03 Limpiar datos | Servicio de limpieza con métricas | Completa |
| HU-04 Generar datos de prueba | API y script SQL | Completa para validación local |
| HU-05 Generar predicciones | Modelo de promedio móvil | Completa |
| HU-06 Visualizar predicciones | Frontend principal con módulo predictivo | Integrada |
| HU-07 Consultar métricas | Endpoint `/api/predictions/metrics` y métricas en UI | Integrada |
| HU-MDRT-002 | Servicio predictivo NoSQL, gateway, MongoDB e ingesta por `inventory-service` | Validada localmente con Docker, MongoDB y endpoints por gateway |
| HU-MDRT-003 | Módulo visual en frontend principal | Validada localmente desde `localhost:3000/predictions` |

## Endpoints oficiales

| Endpoint | Uso |
| --- | --- |
| `GET /api/predictions/health` | Verifica servicio, MongoDB, colecciones y estado del flujo |
| `POST /api/predictions/ingest` | Extrae datos desde `inventory-service` |
| `POST /api/predictions/clean` | Limpia datos crudos y crea `cleaned_data` |
| `POST /api/predictions/train` | Calcula predicciones |
| `POST /api/predictions/recalculate` | Limpia y entrena datos ya cargados |
| `GET /api/predictions` | Lista predicciones |
| `GET /api/predictions/{productId}` | Consulta una predicción puntual |
| `GET /api/predictions/metrics` | Muestra métricas de limpieza y entrenamiento |

## Validación local integrada

La validación más reciente se realizó con backend, frontend, MongoDB y `prediction-service` ejecutándose en Docker. Primero se registraron entradas y salidas por el flujo operativo de FarmaExpres; después se sincronizó inventario desde el módulo predictivo.

Resultado observado:

- `raw_data`: 130 documentos.
- `cleaned_data`: 130 documentos.
- `predictions`: 11 medicamentos evaluados.
- `risk_high_count`: 10 medicamentos en riesgo alto.
- `risk_out_of_stock_count`: 1 medicamento agotado.

## Decisiones técnicas

- Se usa MongoDB porque permite guardar datos crudos, datos limpios, predicciones y métricas sin alterar el modelo relacional.
- Se usa FastAPI porque Python es adecuado para limpieza de datos y analítica inicial.
- Se consume `inventory-service` por HTTP para respetar la propiedad del dominio de inventario.
- Se mantiene `RELATIONAL_DB_URL` únicamente como apoyo local, no como integración oficial.
- Se usa promedio móvil porque es simple, explicable y suficiente para una primera predicción con pocos datos reales.
- Se usa `motion.type = 'Exit'` como demanda aproximada porque no se encontró una tabla formal de ventas u órdenes en el backend actual.
- Se agregan plantillas `.env.dev.example`, `.env.qa.example` y `.env.main.example` para seguir el patrón de ambientes del proyecto.
- Se agregan `.env.dev`, `.env.qa` y `.env.main` versionados para que un clon limpio pueda levantar el microservicio sin reconstruir manualmente la configuración local.

## Despliegue por ambiente

El orden de ejecución validado es:

```bash
cd FarmaExpres_Backend
docker compose --env-file .env.dev up -d --build

cd ../FarmaExpres-Micro-NoSQL
docker compose --env-file .env.dev up -d --build

cd ../FarmaExpres-Frontend/frontend
docker compose --env-file .env.dev up -d --build
```

Para `qa` o `main`, se cambia `.env.dev` por `.env.qa` o `.env.main` en los tres repositorios. Cada ambiente conserva su propia red Docker, puertos publicados y base MongoDB.

## Limitaciones conocidas

- Las salidas de inventario no son ventas reales confirmadas.
- El modelo no contempla estacionalidad avanzada ni eventos externos.
- La generación de datos de prueba no debe usarse como información productiva.
- El promedio móvil debe evolucionar cuando exista más historial real o una tabla formal de ventas.
- El error medio del modelo requiere historial distribuido en varios días para ser más representativo.
