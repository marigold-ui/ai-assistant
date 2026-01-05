# PostgreSQL + pgvector Database Setup

PostgreSQL 16 mit pgvector Extension für Vector Similarity Search.

## Quick Start

```bash
cd etl/docker
docker-compose up -d
```

## Connection

```
Host: localhost
Port: 5432
Database: marigold_rag
User: postgres
Password: postgres
```

## Environment Variables

Alle Einstellungen in `.env` konfigurierbar:

- `DB_HOST`: Database Host
- `DB_PORT`: Database Port
- `DB_NAME`: Database Name
- `DB_USER`: Postgres User
- `DB_PASSWORD`: Postgres Password

## Postgres Shell

```bash
docker exec -it marigold-postgres psql -U postgres -d marigold_rag
```

## Shutdown

```bash
docker-compose down
```

## Volumes

Daten werden in `postgres_data` Volume gespeichert und bleiben nach Restart erhalten.
