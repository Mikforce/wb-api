FROM python:3.11-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запуск FastAPI и бота через скрипт
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 & python bot.py"]