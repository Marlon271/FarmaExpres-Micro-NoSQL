# HU-05 - Generar predicciones

## Historia

Como usuario del sistema, quiero obtener predicciones sobre demanda o inventario de medicamentos, con el fin de anticipar necesidades futuras.

## Contexto

La primera versión usa una técnica simple y explicable: promedio móvil de 30 días con las salidas históricas. El resultado no promete exactitud comercial; sirve como indicador inicial de reposición.

## Alcance

- Calcular demanda estimada para 7 días.
- Estimar días hasta agotamiento cuando exista consumo histórico.
- Clasificar riesgo como `LOW`, `MEDIUM`, `HIGH` u `OUT_OF_STOCK`.

## Criterios de aceptación

- `POST /train` genera predicciones.
- `GET /predictions` lista resultados.
- `GET /predictions/{productId}` consulta un producto puntual.
