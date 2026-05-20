# HU-MDRT-002 - Integrar servicio predictivo NoSQL

## Historia

Como desarrollador de FarmaExpres, quiero integrar un microservicio predictivo con MongoDB al ecosistema existente, con el fin de extraer datos desde `inventory-service`, limpiarlos y generar predicciones sin modificar directamente la base relacional.

## Alcance

- Exponer rutas bajo `/api/predictions`.
- Mantener `api-gateway` como punto oficial de entrada.
- Validar JWT y roles en `prediction-service`.
- Consumir `GET /api/inventory/analytics/snapshot`.
- Guardar productos, lotes y movimientos en MongoDB.
- Mantener `RELATIONAL_DB_URL` solo como fallback local.
- Reemplazar el dataset activo de entrenamiento cuando llega un nuevo snapshot.
- Conservar `/health` para diagnóstico local.

## Criterios de aceptación

- `GET /api/predictions/health` responde por el gateway.
- Las rutas de negocio requieren token.
- El gateway tiene fallback para `prediction-service`.
- `POST /api/predictions/ingest` usa `source=inventory` por defecto.
- El token del usuario se reenvía a `inventory-service`.
- MongoDB guarda `raw_data` y `products_snapshot`.
- La sincronización puede repetirse sin fallar por duplicados en `products_snapshot`.
- La documentación explica que MongoDB no se conecta solo a PostgreSQL.

## Trazabilidad

- Backend: ruta en `api-gateway` y endpoint de snapshot en `inventory-service`.
- Microservicio: router FastAPI `/api/predictions`, cliente HTTP interno y mapeo a documentos MongoDB.
- MongoDB: colecciones `raw_data`, `cleaned_data`, `products_snapshot`, `predictions` y `model_metrics`.
- Documentación: libro NoSQL, integración local y explicación del modelo.
