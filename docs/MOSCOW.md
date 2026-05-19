# MoSCoW y alcance

## Must have - Se hizo

- MongoDB en Docker Compose con volumen persistente.
- Backend FastAPI con endpoints de salud, ingesta, limpieza, entrenamiento, predicciones y métricas.
- Rutas oficiales bajo `/api/predictions` para consumo por gateway.
- Colecciones `raw_data`, `cleaned_data`, `predictions`, `model_metrics` y `products_snapshot`.
- Extracción oficial desde `inventory-service` mediante contrato HTTP interno.
- Generación de datos de prueba amplia para validación local.
- Limpieza inicial: duplicados, nombres, fechas, cantidades negativas, stock y registros incompletos.
- Predicción inicial de demanda a 7 días usando promedio móvil de 30 días.
- Riesgo de agotamiento por producto.
- Módulo visual en el frontend principal.
- Documentación de ejecución por plantillas `.env.dev.example`, `.env.qa.example` y `.env.main.example`.

## Should have - Falta por mejorar

- Ingesta periódica automática programada.
- Separar ventas reales de ajustes cuando el backend tenga una tabla formal de ventas u órdenes.
- Mejorar métricas con validación temporal más clara y comparación por producto.
- Agregar filtros por categoría, riesgo y horizonte de predicción.
- Ampliar pruebas automatizadas de endpoints y contrato entre servicios.

## Could have - Podría agregarse después

- Modelo con regresión lineal o scikit-learn si hay más datos reales.
- Exportación CSV/Excel de predicciones.
- Alertas por vencimiento combinadas con demanda.
- Entrenamiento diario controlado por tarea programada.
- Versionado formal de modelos.

## Won't have for now - No se completó en esta versión

- No se reemplaza PostgreSQL como base operativa.
- No se entrena un modelo avanzado de machine learning.
- No se usan datos reales de producción.
- No se exponen credenciales ni conexión directa a MongoDB para usuarios finales.
- No se trata `RELATIONAL_DB_URL` como integración oficial; queda solo como fallback local.
