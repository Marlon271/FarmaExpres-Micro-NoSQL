# HU-03 - Limpiar datos importados

## Historia

Como sistema, quiero limpiar y normalizar los datos importados, con el fin de evitar errores en el modelo predictivo.

## Contexto

Los datos pueden venir de SQL o de datos simulados. Antes de predecir, se necesita quitar ruido y dejar señales consistentes por producto, fecha y cantidad.

## Alcance

- Eliminar duplicados.
- Normalizar nombres de medicamentos.
- Convertir fechas a formato estándar.
- Validar cantidades negativas, stock negativo y campos incompletos.
- Marcar registros inválidos sin ocultar que existieron.

## Criterios de aceptación

- `POST /clean` procesa `raw_data`.
- Los datos válidos e inválidos quedan en `cleaned_data` con banderas de calidad.
- La respuesta indica registros de entrada, limpios, válidos, inválidos y duplicados removidos.
