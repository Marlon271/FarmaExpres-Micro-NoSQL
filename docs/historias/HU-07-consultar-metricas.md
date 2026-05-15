# HU-07 - Consultar métricas del modelo

## Historia

Como desarrollador, quiero consultar métricas básicas del modelo predictivo, con el fin de evaluar si las predicciones son útiles.

## Contexto

El modelo inicial es simple. Aun así debe mostrar señales mínimas para saber cuántos registros usó y qué tan lejos estuvo en una validación básica.

## Alcance

- Guardar métricas de limpieza.
- Guardar métricas de entrenamiento.
- Mostrar fecha, método, productos evaluados, registros válidos y error medio aproximado.

## Criterios de aceptación

- `GET /metrics` devuelve la última limpieza y el último entrenamiento.
- El frontend muestra el error medio cuando exista.
- La documentación explica que la métrica es aproximada y mejorable.
