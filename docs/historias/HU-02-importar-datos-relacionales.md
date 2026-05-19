# HU-02 - Importar datos desde la base relacional

## Historia

Como desarrollador, quiero traer datos relevantes desde la base relacional del backend, con el fin de usarlos como entrada para limpieza y análisis predictivo.

## Contexto

La base relacional útil para predicción está en `farmaexpres_inventory`. Las tablas revisadas son `product`, `batch` y `motion`. No se encontró una tabla formal de ventas, por eso las salidas de inventario (`Exit`) se tratan como demanda aproximada.

## Alcance

- Leer PostgreSQL solo cuando `RELATIONAL_DB_URL` esté configurada como apoyo local.
- Guardar los registros importados en `raw_data`.
- Guardar productos actuales en `products_snapshot`.

## Criterios de aceptación

- `POST /ingest` acepta `{"source":"postgres"}`.
- Si PostgreSQL no está configurado, el endpoint usa datos generados para no bloquear la validación local.
- La integración oficial debe consumir `inventory-service`, no tablas relacionales directamente.
