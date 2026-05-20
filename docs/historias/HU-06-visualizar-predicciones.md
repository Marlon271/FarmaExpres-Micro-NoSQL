# HU-06 - Visualizar predicciones

## Historia

Como usuario, quiero ver las predicciones en una interfaz simple, con el fin de entender los resultados del modelo sin usar consola.

## Contexto

La vista no busca reemplazar el frontend principal. Es un tablero de validación para mostrar que el microservicio funciona.

## Alcance

- Mostrar estado del servicio y del flujo.
- Mostrar mensajes al cargar, limpiar y predecir.
- Mostrar tabla, gráfica y prioridad de reposición.

## Criterios de aceptación

- El frontend principal corre por Docker y muestra el módulo de predicciones desde la interfaz de FarmaExpres.
- El botón de estado muestra si MongoDB y la API están disponibles.
- El tablero explica que se predice: demanda esperada a 7 días y riesgo de agotamiento.
