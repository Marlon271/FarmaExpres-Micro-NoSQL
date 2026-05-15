# HU-01 - Crear base de datos no relacional

## Historia

Como desarrollador de FarmaExpres, quiero crear una base de datos MongoDB para almacenar datos procesados del sistema, con el fin de tener una fuente flexible para análisis y predicciones.

## Contexto

El backend principal trabaja con PostgreSQL y Liquibase. Este módulo necesita una base separada para guardar datos crudos, datos limpios, predicciones y métricas sin cambiar la estructura relacional actual.

## Alcance

- Crear MongoDB en Docker Compose.
- Crear colecciones usadas por el flujo predictivo.
- Mantener la persistencia en un volumen Docker.

## Criterios de aceptación

- `docker compose --env-file .env.dev up -d --build` levanta MongoDB.
- `GET /health` confirma conexión a MongoDB.
- Existen conteos para `raw_data`, `cleaned_data`, `predictions`, `model_metrics` y `products_snapshot`.
