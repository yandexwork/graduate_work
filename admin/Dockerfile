FROM python:3.10

WORKDIR /app

COPY requirements.txt .
COPY django_project .

RUN pip install -r requirements.txt --no-cache-dir
