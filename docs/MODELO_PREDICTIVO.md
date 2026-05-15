# Modelo predictivo inicial

Este primer modelo no busca ser avanzado. El objetivo es demostrar que los datos se pueden traer, limpiar, guardar en MongoDB y usar para una predicción útil.

## Enfoque

Se usa promedio móvil de 30 días sobre movimientos de salida (`Exit`). En FarmaExpres esos movimientos representan productos que salen del inventario, por eso se usan como aproximación de demanda. Si después existe una tabla de ventas, esa debería reemplazar esta fuente.

## Cálculos

Por producto:

1. Sumar unidades con movimiento `Exit` por día.
2. Tomar los últimos 30 días.
3. Calcular promedio diario.
4. Multiplicar por el horizonte, por defecto 7 días.
5. Comparar con stock actual y stock mínimo.

## Riesgo

- `OUT_OF_STOCK`: stock actual en cero.
- `HIGH`: stock actual no cubre la demanda esperada.
- `MEDIUM`: stock actual está igual o por debajo del mínimo.
- `LOW`: stock suficiente para el horizonte.

## Métricas

Cuando hay suficientes días, se calcula un error absoluto medio aproximado (`average_mae`) comparando cada día contra el promedio de los 7 días anteriores.

Esta métrica es básica, pero sirve para explicar si el modelo está cerca o lejos del comportamiento histórico.

## Mejoras futuras

- Separar ventas reales de ajustes de inventario.
- Agregar estacionalidad por día de semana.
- Usar regresión lineal o scikit-learn cuando existan más datos reales.
- Guardar versiónes del modelo.
- Programar entrenamiento automático.
