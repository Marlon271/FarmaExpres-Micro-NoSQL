# MoSCoW y alcance

## Must have - Se hizo

- MongoDB en Docker Compose con volumen persistente.
- Backend FastAPI con endpoints de salud, ingesta, limpieza, entrenamiento, predicciones y metricas.
- Colecciones `raw_data`, `cleaned_data`, `predictions`, `model_metrics` y `products_snapshot`.
- Generacion de datos de prueba amplia: 80 productos y 180 dias por defecto.
- Limpieza inicial: duplicados, nombres, fechas, cantidades negativas, stock y registros incompletos.
- Prediccion inicial de demanda a 7 dias usando promedio movil de 30 dias.
- Riesgo de agotamiento por producto.
- Frontend pequeno con estado, mensajes del proceso, grafica, tabla y prioridad de reposicion.
- Documentacion de ejecucion por plantillas `.env.dev.example`, `.env.qa.example` y `.env.main.example`.

## Should have - Falta por mejorar

- Ingesta periodica automatica desde PostgreSQL.
- Separar ventas reales de ajustes cuando el backend principal tenga una tabla formal de ventas u ordenes.
- Mejorar metricas con validacion temporal mas clara y comparacion por producto.
- Agregar filtros por categoria, riesgo y horizonte de prediccion.
- Crear pruebas automatizadas de endpoints.

## Could have - Podria agregarse despues

- Modelo con regresion lineal o scikit-learn si hay mas datos reales.
- Exportacion CSV/Excel de predicciones.
- Alertas por vencimiento combinadas con demanda.
- Programar entrenamiento diario.
- Autenticacion si se integra al gateway principal.

## Won't have for now - No se completo en esta version

- No se modifico el backend principal.
- No se creo una integracion definitiva con el API Gateway de FarmaExpres.
- No se entreno un modelo avanzado de machine learning.
- No se usaron datos reales de produccion.
- No se implemento un frontend escalable; es un tablero de validacion del microservicio.
