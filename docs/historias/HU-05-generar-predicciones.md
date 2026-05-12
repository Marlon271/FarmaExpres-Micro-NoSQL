# HU-05 - Generar predicciones

## Historia

Como usuario del sistema, quiero obtener predicciones sobre demanda o inventario de medicamentos, con el fin de anticipar necesidades futuras.

## Contexto

La primera version usa una tecnica simple y explicable: promedio movil de 30 dias con las salidas historicas. El resultado no promete exactitud comercial; sirve como indicador inicial de reposicion.

## Alcance

- Calcular demanda estimada para 7 dias.
- Estimar dias hasta agotamiento cuando exista consumo historico.
- Clasificar riesgo como `LOW`, `MEDIUM`, `HIGH` u `OUT_OF_STOCK`.

## Criterios de aceptacion

- `POST /train` genera predicciones.
- `GET /predictions` lista resultados.
- `GET /predictions/{productId}` consulta un producto puntual.
