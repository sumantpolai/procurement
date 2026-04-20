# Docker Setup

## Quick Start

1. Build and start the containers:
```bash
docker-compose up --build
```

2. Access the API:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Commands

Start containers:
```bash
docker-compose up -d
```

Stop containers:
```bash
docker-compose down
```

View logs:
```bash
docker-compose logs -f app
```

Rebuild after code changes:
```bash
docker-compose up --build
```

Access database:
```bash
docker exec -it procurement_db psql -U postgres -d procurementdb
```

## Environment Variables

The docker-compose.yml uses these defaults:
- Database: procurementdb
- User: postgres
- Password: 2003
- Port: 5432 (PostgreSQL), 8000 (API)
