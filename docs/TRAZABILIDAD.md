# Trazabilidad del microservicio NoSQL

Este documento conecta los objetivos solicitados con los entregables implementados en el repositorio.

## Resumen

El microservicio creado funciona como un modulo independiente de FarmaExpres para:

- almacenar datos procesados en MongoDB,
- limpiar datos crudos,
- generar datos de prueba,
- calcular predicciones simples de demanda,
- visualizar resultados en un tablero pequeno,
- documentar ejecucion, endpoints, historias y alcance.

No se modifico el backend principal. El backend de FarmaExpres solo se usa como referencia y posible fuente local de datos relacionales.

## Trazabilidad por objetivo

| Objetivo | Implementacion | Evidencia |
| --- | --- | --- |
| Crear una base no relacional | MongoDB en Docker Compose con volumen persistente | `docker-compose.yml`, coleccion `raw_data`, `cleaned_data`, `predictions`, `model_metrics`, `products_snapshot` |
| Disenar colecciones NoSQL | Colecciones creadas y usadas desde el backend | `backend/app/database.py` |
| Cargar datos desde fuente relacional o pruebas | Ingesta desde PostgreSQL o datos simulados | `POST /ingest`, `POST /seed-test-data`, `backend/app/services/ingestion.py` |
| Generar muchos datos de prueba | 80 productos y 180 dias por defecto; SQL opcional para PostgreSQL | `backend/app/services/sample_data.py`, `scripts/generate_relational_test_data.py` |
| Limpiar datos | Normalizacion, validacion, duplicados y banderas de calidad | `POST /clean`, `backend/app/services/cleaning.py` |
| Crear modelo predictivo inicial | Promedio movil de 30 dias sobre salidas de inventario | `POST /train`, `backend/app/services/prediction.py` |
| Visualizar resultados | Tablero con estado, mensajes, grafica, tabla y prioridad de reposicion | `frontend/index.html`, `frontend/app.js`, `frontend/styles.css` |
| Documentar historias | HU separadas y explicadas | `docs/HISTORIAS_USUARIO.md`, `docs/historias/*.md` |
| Documentar endpoints | Endpoints, proposito y respuestas esperadas | `docs/ENDPOINTS.md` |
| Documentar modelo | Explicacion del metodo, riesgo y limitaciones | `docs/MODELO_PREDICTIVO.md` |
| Documentar integracion | Ejecucion con `FarmaExpres_Backend` usando `.env.dev` | `docs/INTEGRACION_LOCAL.md`, `README.md` |
| Documentar alcance | MoSCoW: hecho, pendiente y no incluido | `docs/MOSCOW.md` |

## Trazabilidad por historia de usuario

| Historia | Entregable principal | Estado |
| --- | --- | --- |
| HU-01 Base de datos NoSQL | MongoDB + colecciones + health check | Completa |
| HU-02 Importar datos relacionales | Ingesta PostgreSQL por `RELATIONAL_DB_URL` | Completa para pruebas locales |
| HU-03 Limpiar datos | Servicio de limpieza con metricas | Completa |
| HU-04 Generar datos de prueba | API y script SQL | Completa |
| HU-05 Generar predicciones | Modelo de promedio movil | Completa |
| HU-06 Visualizar predicciones | Frontend operativo | Completa |
| HU-07 Consultar metricas | Endpoint `/metrics` y metrica en UI | Completa |

## Endpoints implementados

| Endpoint | Uso |
| --- | --- |
| `GET /health` | Verifica backend, MongoDB, colecciones y estado del flujo |
| `POST /seed-test-data` | Genera datos simulados para MongoDB |
| `POST /ingest` | Carga datos simulados o desde PostgreSQL |
| `POST /clean` | Limpia datos crudos y crea `cleaned_data` |
| `POST /train` | Calcula predicciones |
| `GET /predictions` | Lista predicciones |
| `GET /predictions/{productId}` | Consulta una prediccion puntual |
| `GET /metrics` | Muestra metricas de limpieza y entrenamiento |

## Pruebas locales realizadas

Comando de ejecucion usado:

```bash
docker compose --env-file .env.dev up -d --build
```

Resultado validado:

| Validacion | Resultado |
| --- | --- |
| Contenedores dev | MongoDB, backend y frontend activos |
| Health | `status: ok` |
| Datos crudos | `15310` registros |
| Datos limpios | `15230` registros |
| Predicciones | `80` productos |
| Registros validos usados | `15150` |
| Duplicados removidos | `80` |
| Error medio aproximado | `2.56` |
| Riesgo alto | `25` productos |

## Decisiones tecnicas

- Se usa MongoDB porque permite guardar datos crudos, datos limpios, predicciones y metricas sin alterar el modelo relacional.
- Se usa FastAPI porque permite crear endpoints claros y livianos para una primera version.
- Se usa promedio movil porque es simple, explicable y suficiente para demostrar prediccion inicial con pocos datos reales.
- Se usa `motion.type = 'Exit'` como demanda aproximada porque no se encontro una tabla formal de ventas u ordenes en el backend actual.
- Se agregan plantillas `.env.dev.example`, `.env.qa.example` y `.env.main.example` para seguir el patron del backend principal sin publicar configuraciones locales.

## Limitaciones conocidas

- Las salidas de inventario no son ventas reales confirmadas.
- El modelo no contempla estacionalidad avanzada ni eventos externos.
- La interfaz es un tablero de validacion, no un frontend final del ecosistema.
- La integracion con el API Gateway principal queda como trabajo futuro.
