url in .env `DATABASE_URL`

_in services/task_database_

1. Up database server in docker

- `root# docker-compose up`

2. Check and init:

- `root# docker exec -it task_database-db-1 psql -U user -d task_planner_db`
- `CREATE DATABASE task_planner_db;`
- `CREATE USER usr WITH PASSWORD 'password';`
- `GRANT ALL PRIVILEGES ON DATABASE task_planner_db TO user;`
- `CREATE EXTENSION vector;`
- `\q`

3. Init alembic

- `uv run alembic init`
- `uv run alembic revision --autogenerate -m "Create tasks table1"`
- `uv run alembic upgrade head`

4. Run service

- `uv run uvicorn app.main:app`
