FROM python:3.8.5-alpine

RUN pip install --upgrade pip

RUN apk add --no-cache libpq

COPY ./requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY ./django_project /app

WORKDIR /app

ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"] 

