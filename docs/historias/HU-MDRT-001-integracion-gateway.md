# HU-MDRT-001 - Integrar prediction-service al gateway

## Historia

Como usuario de FarmaExpres, quiero consultar predicciones desde el portal principal, con el fin de no entrar a una aplicación separada para revisar demanda e inventario.

## Alcance

- Exponer rutas bajo `/api/predictions`.
- Mantener `api-gateway` como punto oficial de entrada.
- Validar JWT y roles en `prediction-service`.
- Conservar `/health` para diagnóstico local.

## Criterios de aceptación

- `GET /api/predictions/health` responde por el gateway.
- Las rutas de negocio requieren token.
- El gateway tiene fallback para `prediction-service`.
- La documentación explica que el frontend oficial consume rutas relativas `/api/predictions`.

## Trazabilidad

- Backend: ruta en `api-gateway`.
- Microservicio: router FastAPI `/api/predictions`.
- Frontend: módulo `Predicciones`.
