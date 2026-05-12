# HU-07 - Consultar metricas del modelo

## Historia

Como desarrollador, quiero consultar metricas basicas del modelo predictivo, con el fin de evaluar si las predicciones son utiles.

## Contexto

El modelo inicial es simple. Aun asi debe mostrar senales minimas para saber cuantos registros uso y que tan lejos estuvo en una validacion basica.

## Alcance

- Guardar metricas de limpieza.
- Guardar metricas de entrenamiento.
- Mostrar fecha, metodo, productos evaluados, registros validos y error medio aproximado.

## Criterios de aceptacion

- `GET /metrics` devuelve la ultima limpieza y el ultimo entrenamiento.
- El frontend muestra el error medio cuando exista.
- La documentacion explica que la metrica es aproximada y mejorable.
