# HU-MDRT-002 - Sincronizar datos desde inventory-service

## Historia

Como desarrollador de FarmaExpres, quiero que el servicio predictivo obtenga datos desde `inventory-service`, con el fin de respetar la propiedad de datos del backend y evitar consultas directas al esquema relacional.

## Alcance

- Consumir `GET /api/inventory/analytics/snapshot`.
- Guardar productos, lotes y movimientos en MongoDB.
- Mantener `RELATIONAL_DB_URL` solo como fallback local.
- Limpiar colecciones derivadas cuando entra un nuevo snapshot.

## Criterios de aceptación

- `POST /api/predictions/ingest` usa `source=inventory` por defecto.
- El token del usuario se reenvía a `inventory-service`.
- MongoDB guarda `raw_data` y `products_snapshot`.
- La documentación indica que MongoDB no se conecta solo a PostgreSQL.

## Trazabilidad

- Backend: endpoint de snapshot en `inventory-service`.
- Microservicio: cliente HTTP interno y mapeo a documentos MongoDB.
- Documentación: libro NoSQL e integración local.
