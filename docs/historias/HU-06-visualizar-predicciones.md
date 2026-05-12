# HU-06 - Visualizar predicciones

## Historia

Como usuario, quiero ver las predicciones en una interfaz simple, con el fin de entender los resultados del modelo sin usar consola.

## Contexto

La vista no busca reemplazar el frontend principal. Es un tablero de validacion para mostrar que el microservicio funciona.

## Alcance

- Mostrar estado del servicio y del flujo.
- Mostrar mensajes al cargar, limpiar y predecir.
- Mostrar tabla, grafica y prioridad de reposicion.

## Criterios de aceptacion

- El frontend corre por Docker en `http://localhost:5174`.
- El boton de estado muestra si MongoDB y la API estan disponibles.
- El tablero explica que se predice: demanda esperada a 7 dias y riesgo de agotamiento.
