# Modelo predictivo inicial

Este primer modelo no busca ser avanzado. El objetivo es demostrar que los datos se pueden traer, limpiar, guardar en MongoDB y usar para una prediccion util.

## Enfoque

Se usa promedio movil de 30 dias sobre movimientos de salida (`Exit`). En FarmaExpres esos movimientos representan productos que salen del inventario, por eso se usan como aproximacion de demanda. Si despues existe una tabla de ventas, esa deberia reemplazar esta fuente.

## Calculos

Por producto:

1. Sumar unidades con movimiento `Exit` por dia.
2. Tomar los ultimos 30 dias.
3. Calcular promedio diario.
4. Multiplicar por el horizonte, por defecto 7 dias.
5. Comparar con stock actual y stock minimo.

## Riesgo

- `OUT_OF_STOCK`: stock actual en cero.
- `HIGH`: stock actual no cubre la demanda esperada.
- `MEDIUM`: stock actual esta igual o por debajo del minimo.
- `LOW`: stock suficiente para el horizonte.

## Metricas

Cuando hay suficientes dias, se calcula un error absoluto medio aproximado (`average_mae`) comparando cada dia contra el promedio de los 7 dias anteriores.

Esta metrica es basica, pero sirve para explicar si el modelo esta cerca o lejos del comportamiento historico.

## Mejoras futuras

- Separar ventas reales de ajustes de inventario.
- Agregar estacionalidad por dia de semana.
- Usar regresion lineal o scikit-learn cuando existan mas datos reales.
- Guardar versiones del modelo.
- Programar entrenamiento automatico.
