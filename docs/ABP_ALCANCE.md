# ABP y alcance del proyecto

Este documento resume el alcance del microservicio desde una mirada de Aprendizaje Basado en Problemas. Sirve para explicar qué problema se abordó, qué solución se construyó y qué queda fuera de esta primera versión.

## Problema

FarmaExpres tiene información operativa en una base relacional, pero para el nuevo corte se necesitaba demostrar uso de base de datos no relacional, limpieza de datos y predicción. El reto era hacerlo sin modificar el backend principal.

## Pregunta guía

¿Cómo puede FarmaExpres usar una base no relacional para preparar datos de inventario y generar una predicción inicial de demanda sin afectar su sistema principal?

## Objetivo general

Construir un microservicio independiente que use MongoDB para almacenar datos crudos, datos limpios, predicciones y métricas, permitiendo visualizar una estimación de demanda e inventario.

## Objetivos específicos

- Revisar la estructura del backend principal y sus datos relacionales.
- Extraer o simular datos de productos, lotes y movimientos.
- Guardar esos datos en MongoDB.
- Limpiar y validar los registros antes de usarlos.
- Calcular una predicción inicial con un método simple y explicable.
- Mostrar el resultado en un frontend pequeño.
- Documentar el flujo para que pueda sustentarse de forma clara.

## Alcance de esta versión

Sí incluye:

- Docker Compose con MongoDB, backend y frontend.
- API FastAPI con endpoints de ingesta, limpieza, entrenamiento, predicciones y métricas.
- Colecciones MongoDB para cada etapa del dato.
- Datos de prueba amplios.
- Predicción por promedio móvil de 30 días.
- Tablero visual para explicar el flujo y consultar resultados.
- Documentación técnica y pedagógica.

No incluye:

- Cambios en el backend principal.
- Integración definitiva con el API Gateway.
- Autenticación del microservicio.
- Modelo avanzado de machine learning.
- Uso de datos reales de producción.

## Metodología usada

1. Revisión del backend principal para entender Docker, Liquibase y tablas.
2. Identificación de tablas útiles para inventario.
3. Diseño de colecciones NoSQL según el ciclo del dato.
4. Implementación de ingesta desde PostgreSQL o datos generados.
5. Implementación de limpieza y banderas de calidad.
6. Implementación de promedio móvil como modelo inicial.
7. Construcción de frontend de validación.
8. Documentación de historias, alcance, endpoints y flujo NoSQL.

## Entregables

| Entregable | Estado |
| --- | --- |
| Repositorio independiente | Completo |
| Base MongoDB | Completo |
| Backend predictivo | Completo |
| Frontend de visualización | Completo |
| Datos de prueba | Completo |
| Documentación ABP y NoSQL | Completo |
| Integración definitiva con FarmaExpres | Pendiente |

## Conclusión

El proyecto demuestra que FarmaExpres puede tener un módulo analítico separado del sistema principal. PostgreSQL sigue siendo la base operativa, mientras MongoDB se usa como base flexible para análisis, limpieza, predicción y visualización.

