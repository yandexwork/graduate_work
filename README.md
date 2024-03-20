# Платежный сервис

Сервис по оплате услуг. Реализована оплата подписок с автоматическим продлением, а также возврат денежных средств. Добавить и настроить тарифы можно с помощью админ панели.
Стек: Python, FastAPI, Django, Postgres, Alembic, sqlalchemy, yookassa, Celery, Redis, Docker, Nginx.

## Развертывание приложения
1. Заполнить .env файл
2. Запустить docker: docker compose build && docker compose down && docker compose up -d

## Дополнительно:
- alembic revision --autogenerate -m "your-comment"
- Запустить тесты: pytest -s
