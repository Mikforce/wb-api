from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy.orm import Session
from models import User, get_db, Product
import asyncio
import logging
from dotenv import load_dotenv
import os
import requests

# Загрузка переменных окружения
load_dotenv()
logging.basicConfig(level=logging.INFO)

# Получение токена бота
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

from sqlalchemy.exc import IntegrityError

@dp.message(Command("start"))
async def send_welcome(message: Message):
    chat_id = message.chat.id
    db: Session = next(get_db())  # Получаем сессию базы данных

    try:
        # Проверяем, существует ли пользователь
        user = db.query(User).filter(User.chat_id == chat_id).first()
        if not user:
            # Создаем нового пользователя
            new_user = User(chat_id=chat_id)
            db.add(new_user)
            db.commit()
            await message.answer("Вы зарегистрированы! Теперь вы будете получать уведомления.")
        else:
            await message.answer("Вы уже зарегистрированы.")
    except IntegrityError as e:
        db.rollback()  # Откатываем транзакцию в случае ошибки
        logging.error(f"Ошибка при регистрации пользователя: {e}")
        await message.answer("Вы уже зарегистрированы.")
    except Exception as e:
        logging.error(f"Ошибка при регистрации пользователя: {e}")
        await message.answer("Произошла ошибка при регистрации.")
    finally:
        db.close()  # Закрываем сессию

# Обработчик команды /track
@dp.message(Command("track"))
async def track_product(message: Message):
    try:
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
    except Exception as e:
        logging.error(f"Ошибка при обработке команды /track: {e}")
        await message.reply("Произошла ошибка при обработке запроса.")

# Функция для отправки сообщений пользователю
async def send_message_to_user(chat_id: int, message: str):
    try:
        await bot.send_message(chat_id, message)
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения {chat_id}: {e}")

# Основная функция для запуска бота
async def main():
    await dp.start_polling(bot)

# Точка входа
if __name__ == '__main__':
    asyncio.run(main())