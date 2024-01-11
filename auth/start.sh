poetry run alembic upgrade head
poetry run uvicorn --reload --host 0.0.0.0 --port 8000 src.main:app