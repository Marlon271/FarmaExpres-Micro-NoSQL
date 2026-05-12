# Arquitectura y analisis inicial

## Repos revisados

Se clono `https://github.com/FarmaExpres/FarmaExpres.git` como referencia general. Ese repositorio funciona como hub/documentacion del ecosistema y no trae el backend operativo ni `docker-compose.yml` del sistema.

La referencia tecnica local que si contiene backend, Docker, Liquibase y tablas es `../FarmaExpres_Backend`.

Tambien se revisaron ramas remotas de backend y frontend. Ambos usan `Develop`, `QA` y `main`, por eso este repositorio nuevo se dejo trabajando en `Develop`.

## Como corre el backend principal

El backend principal se ejecuta desde `FarmaExpres_Backend` con:

```bash
docker compose --env-file .env.dev up -d --build
```

Tambien existen plantillas para `.env.qa` y `.env.main`. La diferencia esta en los puertos publicados al host:

- `dev`: gateway `8080`, inventory `8082`, postgres `5433`.
- `qa`: gateway `9080`, inventory `9082`, postgres `6433`.
- `main`: gateway `10080`, inventory `10082`, postgres `7433`.

Dentro de Docker los servicios conservan sus puertos internos; por ejemplo PostgreSQL sigue en `5432` dentro de la red de contenedores.

Servicios principales:

- `postgres`: PostgreSQL 16 en puerto externo `5433`.
- `liquibase-auth`: aplica migraciones de usuarios.
- `liquibase-inventory`: aplica migraciones de inventario.
- `auth-service`: Spring Boot en `8081`.
- `inventory-service`: Spring Boot en `8082`.
- `alert-service`: Node/Express en `8083`.
- `api-gateway`: Spring Boot en `8080`.

## Donde esta el backend

En `FarmaExpres_Backend`:

- `auth-service/`
- `inventory-service/`
- `alert-service/`
- `api-gateway/`

## Donde esta Liquibase

Liquibase esta versionado en:

- `database/auth/changelog-master.yaml`
- `database/inventory/changelog-master.yaml`
- `database/auth/01_ddl`
- `database/auth/02_dml`
- `database/inventory/01_ddl`
- `database/inventory/02_dml`

Docker Compose monta `./database` y ejecuta los contenedores `liquibase-auth` y `liquibase-inventory` antes de levantar los servicios.

## Tablas relacionales utiles

Base `farmaexpres_inventory`:

- `product`: medicamentos, codigo, stock, precio, stock minimo, fecha de vencimiento y datos farmaceuticos.
- `batch`: lotes por producto, stock inicial, stock disponible y fecha de vencimiento.
- `motion`: movimientos de inventario. El tipo `Exit` se toma como salida/venta simulada para demanda; `Entrance` como reposicion.

Base `farmaexpres_users`:

- `role`: roles.
- `users`: usuarios del sistema.
- `binnacle`: auditoria de acciones.
- `refresh_token`: tokens de sesion.

No se encontro una tabla especifica de ventas u ordenes en la estructura actual. Para el primer modelo se usa `motion.type = 'Exit'` como aproximacion de demanda o venta.

## Datos utiles para el modelo predictivo

- Nombre, codigo y categoria del producto.
- Stock actual y stock minimo.
- Lotes y vencimientos.
- Movimientos historicos por fecha.
- Cantidades de salida (`Exit`) por producto.
- Entradas (`Entrance`) para entender reposicion.

Con esos campos se puede estimar demanda por promedio movil, productos con mayor salida y riesgo de agotamiento. No se afirma que sean ventas reales porque la tabla disponible es de movimientos de inventario.

## Arquitectura del nuevo microservicio

```text
Frontend estatico
  -> FastAPI backend
      -> MongoDB
      -> PostgreSQL FarmaExpres solo en modo pruebas locales
```

Colecciones MongoDB:

- `raw_data`: datos crudos importados o generados.
- `cleaned_data`: datos normalizados y validados.
- `predictions`: predicciones por producto.
- `model_metrics`: metricas de limpieza y entrenamiento.
- `products_snapshot`: copia de productos relevante para el analisis.

El microservicio no modifica el backend principal. Solo lee datos si se configura la conexion relacional.
