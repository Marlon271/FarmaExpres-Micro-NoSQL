# HU-04 - Generar datos de prueba

## Historia

Como desarrollador, quiero inyectar una cantidad considerable de datos de prueba, con el fin de validar el comportamiento del modelo predictivo.

## Contexto

La semilla actual del backend tiene pocos medicamentos y pocos movimientos. Para demostrar analitica se necesitan mas productos y mas historial.

## Alcance

- Generar 80 medicamentos y 180 dias de movimientos desde la API.
- Generar SQL opcional para PostgreSQL local.
- Simular entradas, salidas, stock, categorias, lotes y fechas.

## Criterios de aceptacion

- `POST /seed-test-data` carga datos suficientes en MongoDB.
- `scripts/generate_relational_test_data.py` crea SQL para la base `farmaexpres_inventory`.
- La documentacion aclara que los datos no son productivos.
