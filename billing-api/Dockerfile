FROM python:3.10

WORKDIR /app

COPY requirements.txt .
COPY alembic.ini .
COPY ./src .

RUN pip install -r requirements.txt