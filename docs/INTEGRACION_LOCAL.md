# Integración local con FarmaExpres

## Objetivo

Probar este microservicio sin tocar el backend principal. El backend principal solo se usa como fuente de datos relacional local.

## Pasos

1. Entrar al backend principal:

```bash
cd ../FarmaExpres_Backend
```

2. Levantar servicios:

```bash
docker compose --env-file .env.dev up -d --build
```

Si `docker` no está en el PATH:

```bash
/Applications/Docker.app/Contents/Resources/bin/docker compose --env-file .env.dev up -d --build
```

3. Confirmar PostgreSQL:

```bash
docker compose ps
```

PostgreSQL debe quedar disponible en `localhost:5433`.

4. Volver a este repo y levantar el microservicio:

```bash
cd ../FarmaExpres-Micro-NoSQL
cp .env.dev.example .env.dev
docker compose --env-file .env.dev up -d --build
```

Antes de usar la ingesta desde PostgreSQL, reemplazar `CHANGE_ME` en `.env.dev` por la clave local de PostgreSQL. Si solo se van a probar datos simulados, `RELATIONAL_DB_URL` puede quedar vacío.

5. Ingestar desde PostgreSQL:

```bash
curl -X POST http://localhost:8000/ingest -H "Content-Type: application/json" -d '{"source":"postgres"}'
curl -X POST http://localhost:8000/clean
curl -X POST http://localhost:8000/train
```

6. Abrir frontend:

```text
http://localhost:5174
```

## Datos de prueba relacionales

Para crear muchos movimientos de inventario en PostgreSQL local:

```bash
python3 scripts/generate_relational_test_data.py --products 100 --days 180
```

Luego ejecutar el SQL generado contra `farmaexpres_inventory`.

Importante: estos datos son simulados y no se deben tratar como producción.
