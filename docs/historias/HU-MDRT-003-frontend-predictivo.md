# HU-MDRT-003 - Visualizar predicciones en el portal principal

## Historia

Como administrador, farmacéutico o auditor, quiero ver predicciones de demanda dentro del frontend principal, con el fin de anticipar reposición de medicamentos sin usar consola ni tableros externos.

## Alcance

- Agregar módulo `Predicciones` al menú del portal.
- Mostrar estado del servicio, conteos, métricas y tabla.
- Permitir que administrador y auditor sincronicen, limpien y recalculen.
- Permitir que farmacéutico consulte resultados en modo lectura.

## Criterios de aceptación

- El menú muestra `Predicciones` para los roles autorizados.
- El frontend consume `/api/predictions` por gateway.
- La pantalla explica qué predice el modelo y por qué usa salidas de inventario.
- Los mensajes de error y éxito son claros para el usuario.

## Trazabilidad

- Frontend: `frontend/src/predictions`.
- Roles: `canAccessPredictions` y `canManagePredictions`.
- API: servicio Axios `predictions.service.js`.
