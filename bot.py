import logging
import asyncio
import os
import requests
from sqlalchemy.orm import Session
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command  # Импорт Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from dotenv import load_dotenv
from models import User, get_db



# Загрузка переменных окружения из файла .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и хранилища
bot = Bot(token=TELEGRAM_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)  # Исправлено: storage передается как именованный аргумент


# # Обработчик команды /start
# @dp.message(Command("start"))  # Исправлено: использование Command
# async def send_welcome(message: Message):
#     await message.reply("Привет! Я бот для отслеживания товаров с Wildberries.")
# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: Message):
    chat_id = message.chat.id
    db: Session = next(get_db())

    # Проверяем, есть ли пользователь в базе данных
    user = db.query(User).filter(User.chat_id == chat_id).first()
    if not user:
        # Если пользователя нет, добавляем его
        new_user = User(chat_id=chat_id)
        db.add(new_user)
        db.commit()
        await message.answer("Вы зарегистрированы! Теперь вы будете получать уведомления.")
    else:
        await message.answer("Вы уже зарегистрированы.")



# Обработчик команды /track
@dp.message(Command("track"))  # Исправлено: использование Command
async def track_product(message: Message):
    artikul = message.text.split()[1] if len(message.text.split()) > 1 else None
    if not artikul:
        await message.reply("Пожалуйста, укажите артикул товара.")
        return

    url = f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={artikul}"
    response = requests.get(url)
    if response.status_code != 200:
        await message.reply("Товар не найден.")
        return

    data = response.json()
    product_data = data['data']['products'][0]

    product_info = (
        f"Название: {product_data['name']}\n"
        f"Артикул: {artikul}\n"
        f"Цена: {product_data['salePriceU'] / 100} руб.\n"
        f"Рейтинг: {product_data['rating']}\n"
        f"Количество на складах: {sum(stock['qty'] for size in product_data['sizes'] for stock in size.get('stocks', []))}"
    )

    await message.reply(product_info)


# Функция для отправки сообщений пользователю
async def send_message_to_user(chat_id: int, message: str):
    try:
        await bot.send_message(chat_id, message)
    except Exception as e:
        logging.error(f"Error sending message to {chat_id}: {e}")


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())