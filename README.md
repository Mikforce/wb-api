# Проект: Сбор данных с Wildberries и уведомления в Telegram
Этот проект предоставляет API для сбора данных о товарах с Wildberries и отправки уведомлений в Telegram через бота. API построен на FastAPI, а бот использует библиотеку Aiogram.

## Основные функции
Сбор данных о товарах:

По артикулу товара собираются данные: название, цена, рейтинг и количество на складах.

Данные сохраняются в базу данных.

Периодический сбор данных:

Можно подписаться на обновление данных по конкретному артикулу с периодичностью раз в 30 минут.

Уведомления в Telegram:

Пользователи могут зарегистрироваться в боте, и их chat_id будет сохранен в базе данных.

Уведомления отправляются всем зарегистрированным пользователям при обновлении данных.

## Технологии
FastAPI: для создания API.

Aiogram: для создания Telegram-бота.

SQLAlchemy: для работы с базой данных.

APScheduler: для периодического выполнения задач.

SQLite: база данных (можно заменить на PostgreSQL или MySQL).

## Установка и настройка
1. Клонирование репозитория
bash
Copy
git clone https://github.com/Mikforce/wb-api.git
cd ваш-репозиторий
2. Установка зависимостей
Убедитесь, что у вас установлен Python 3.11. Затем установите зависимости:

bash
Copy
pip install -r requirements.txt
3. Настройка переменных окружения
Создайте файл .env в корневой директории проекта и добавьте туда следующие переменные:

env
Copy
TELEGRAM_TOKEN=ваш_токен_бота
DATABASE_URL=postgresql://mouser:mypassword@db:5432/wb_db
TELEGRAM_TOKEN: Токен вашего Telegram-бота (получите у BotFather).


docker-compose.yml

TELEGRAM_TOKEN: Токен вашего Telegram-бота


## Запуск проекта

# Запуск с Docker
1. Сборка и запуск контейнеров
Выполните:

bash
Copy
docker-compose up --build
2. Остановка контейнеров
bash
Copy
docker-compose down -v


1. Сбор данных по артикулу
Эндпоинт: POST /api/v1/products

## Тело запроса:

json
Copy
{
  "artikul": 211695539
}
Пример запроса:

bash
Copy
curl -X POST "http://localhost:8000/api/v1/products" -H "Content-Type: application/json" -d '{"artikul": 123456}'
Ответ:

json
Copy
{
  "message": "Сбор данных запущен"
}
2. Подписка на обновления
Эндпоинт: GET /api/v1/subscribe/{artikul}

Пример запроса:

bash
Copy
curl -X GET "http://localhost:8000/api/v1/subscribe/211695539"
Ответ:

json
Copy
{
  "message": "Подписаны на артикул 211695539"
}
# Использование бота
1. Запуск бота
После запуска бота отправьте команду /start в Telegram. Бот сохранит ваш chat_id в базу данных.

2. Получение уведомлений
Когда данные по подписанному артикулу обновляются, бот отправляет уведомление всем зарегистрированным пользователям.

3. Получение данных по Артикул /track 211695539


## Структура проекта
Copy
wb_tg/
├── main.py                # FastAPI приложение
├── bot.py                 # Telegram бот
├── models.py              # Модели базы данных
├── services.py            # Логика работы с данными
├── requirements.txt       # Зависимости
├── README.md              # Описание проекта
├── .env                   # Переменные окружения
├── Dockerfile             # Dockerfile для сборки контейнера
└── docker-compose.yml     # Docker Compose файл




Автор
[Tolpeev I.V]
