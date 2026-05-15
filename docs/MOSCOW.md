# MoSCoW y alcance

## Must have - Se hizo

- MongoDB en Docker Compose con volumen persistente.
- Backend FastAPI con endpoints de salud, ingesta, limpieza, entrenamiento, predicciones y métricas.
- Colecciones `raw_data`, `cleaned_data`, `predictions`, `model_metrics` y `products_snapshot`.
- Generación de datos de prueba amplia: 80 productos y 180 días por defecto.
- Limpieza inicial: duplicados, nombres, fechas, cantidades negativas, stock y registros incompletos.
- Predicción inicial de demanda a 7 días usando promedio móvil de 30 días.
- Riesgo de agotamiento por producto.
- Frontend pequeño con estado, mensajes del proceso, gráfica, tabla y prioridad de reposición.
- Documentación de ejecución por plantillas `.env.dev.example`, `.env.qa.example` y `.env.main.example`.

## Should have - Falta por mejorar

- Ingesta periódica automática desde PostgreSQL.
- Separar ventas reales de ajustes cuando el backend principal tenga una tabla formal de ventas u órdenes.
- Mejorar métricas con validación temporal más clara y comparación por producto.
- Agregar filtros por categoría, riesgo y horizonte de predicción.
- Crear pruebas automatizadas de endpoints.

## Could have - Podría agregarse después

- Modelo con regresión lineal o scikit-learn si hay más datos reales.
- Exportación CSV/Excel de predicciones.
- Alertas por vencimiento combinadas con demanda.
- Programar entrenamiento diario.
- Autenticación si se integra al gateway principal.

## Won't have for now - No se completó en esta versión

- No se modificó el backend principal.
- No se creó una integración definitiva con el API Gateway de FarmaExpres.
- No se entrenó un modelo avanzado de machine learning.
- No se usaron datos reales de producción.
- No se implementó un frontend escalable; es un tablero de validación del microservicio.
