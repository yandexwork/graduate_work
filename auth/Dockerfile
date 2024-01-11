FROM python:3.10

WORKDIR /app

RUN pip install poetry

COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml

COPY start.sh start.sh
COPY alembic.ini alembic.ini
COPY conftest.py conftest.py
COPY ./src ./src

RUN poetry install --no-root --no-dev

ENTRYPOINT ["/bin/sh", "/app/start.sh"]