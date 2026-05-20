# HU-04 - Generar datos de prueba

## Historia

Como desarrollador, quiero inyectar una cantidad considerable de datos de prueba, con el fin de validar el comportamiento del modelo predictivo.

## Contexto

La semilla actual del backend tiene pocos medicamentos y pocos movimientos. Para demostrar analítica se necesitan más productos y más historial.

## Alcance

- Generar 80 medicamentos y 180 días de movimientos desde la API.
- Generar SQL opcional para PostgreSQL local.
- Simular entradas, salidas, stock, categorías, lotes y fechas.

## Criterios de aceptación

- `POST /seed-test-data` carga datos suficientes en MongoDB.
- `scripts/generate_relational_test_data.py` crea SQL para la base `farmaexpres_inventory`.
- La documentación aclara que los datos no son productivos.
