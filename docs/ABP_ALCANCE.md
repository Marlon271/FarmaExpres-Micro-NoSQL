# ABP y alcance del proyecto

Este documento resume el alcance del microservicio desde una mirada de Aprendizaje Basado en Problemas. Sirve para explicar qué problema se abordó, qué solución se construyó y qué queda fuera de esta primera versión.

## Problema

FarmaExpres tiene información operativa en una base relacional, pero necesita una capa analítica para limpiar datos, preparar información histórica y generar predicciones iniciales de demanda. El reto es hacerlo sin romper la arquitectura de microservicios ni saltarse la propiedad de datos de `inventory-service`.

## Pregunta guía

¿Cómo puede FarmaExpres usar una base no relacional para preparar datos de inventario y generar una predicción inicial de demanda integrada al portal principal?

## Objetivo general

Construir un microservicio analítico que use MongoDB para almacenar datos crudos, datos limpios, predicciones y métricas, consumiendo datos desde `inventory-service` y exponiendo resultados por el `api-gateway`.

## Objetivos específicos

- Revisar la estructura del backend principal y sus datos relacionales.
- Extraer datos de productos, lotes y movimientos desde `inventory-service`.
- Guardar esos datos en MongoDB.
- Limpiar y validar los registros antes de usarlos.
- Calcular una predicción inicial con un método simple y explicable.
- Mostrar el resultado en el frontend principal de FarmaExpres.
- Documentar el flujo para que pueda sustentarse de forma clara.

## Alcance de esta versión

Sí incluye:

- Docker Compose con MongoDB y `prediction-service`.
- API FastAPI con endpoints oficiales bajo `/api/predictions`.
- Colecciones MongoDB para cada etapa del dato.
- Datos de prueba amplios.
- Predicción por promedio móvil de 30 días.
- Módulo visual en el frontend principal.
- Documentación técnica y pedagógica.

No incluye:

- Modelo avanzado de machine learning.
- Uso de datos reales de producción.
- Reemplazo de PostgreSQL como base operativa.
- Lectura directa del esquema `inventory` como integración oficial.

## Metodología usada

1. Revisión del backend principal para entender Docker, Liquibase y tablas.
2. Identificación de tablas útiles para inventario.
3. Diseño de colecciones NoSQL según el ciclo del dato.
4. Implementación de ingesta desde `inventory-service`.
5. Implementación de limpieza y banderas de calidad.
6. Implementación de promedio móvil como modelo inicial.
7. Integración visual en el frontend principal.
8. Documentación de historias, alcance, endpoints y flujo NoSQL.

## Entregables

| Entregable | Estado |
| --- | --- |
| Repositorio del microservicio | Completo |
| Base MongoDB | Completo |
| Backend predictivo | Completo |
| Integración con gateway | En implementación |
| Módulo en frontend principal | En implementación |
| Datos de prueba | Completo |
| Documentación ABP y NoSQL | Completo |
| Integración definitiva con FarmaExpres | En implementación |

## Conclusión

El proyecto integra una capa analítica al ecosistema FarmaExpres. PostgreSQL sigue siendo la base operativa, `inventory-service` conserva la propiedad de los datos de inventario y MongoDB funciona como base flexible para análisis, limpieza, predicción y visualización.
