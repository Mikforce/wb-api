from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from typing import Dict
from sqlalchemy import select
from services import fetch_wb_data, process_wb_data, save_product_to_db
from models import get_db, Product, User
import services
import bot
from database import init_db
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)



app = FastAPI()
init_db()

scheduler = AsyncIOScheduler()

class ProductArtikul(BaseModel):
    artikul: int

async def process_product_data(artikul: int, db: Session):
    try:
        data = await fetch_wb_data(artikul)
        product_data = process_wb_data(data)

        if not product_data:
            raise ValueError(f"Данные для артикула {artikul} не найдены")

        db_product = save_product_to_db(db, product_data)

        if db_product:
            message = f"Данные по товару {artikul} обновлены"
            users = db.query(User).all()
            for user in users:
                await bot.send_message_to_user(user.chat_id, message)
        else:
            message = f"Не удалось обновить данные по товару {artikul}"
            users = db.query(User).all()
            for user in users:
                await bot.send_message_to_user(user.chat_id, message)
    except Exception as e:
        logger.error(f"Ошибка при обработке данных для артикула {artikul}: {e}")

@app.post("/api/v1/products")
async def create_product_data(product: ProductArtikul, background_tasks: BackgroundTasks,
                              db: Session = Depends(get_db)):
    background_tasks.add_task(process_product_data, product.artikul, db)
    return {"message": "Сбор данных запущен"}

@app.get("/api/v1/subscribe/{artikul}")
async def subscribe_to_product(artikul: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    job_id = f'product_update_{artikul}'
    if scheduler.get_job(job_id):
        raise HTTPException(status_code=400, detail="Уже подписан на этот артикул")

    background_tasks.add_task(start_periodic_update, artikul, job_id, db)
    return {"message": f"Подписаны на артикул {artikul}"}

async def start_periodic_update(artikul: int, job_id: str, db: Session):
    scheduler.add_job(
        update_product_data,
        trigger=IntervalTrigger(minutes=30),
        args=[artikul, db],
        id=job_id
    )

async def update_product_data(artikul: int, db: Session):
    db_product = await services.update_product(db, artikul)
    if db_product:
        message = f"Обновлены данные по артикулу {artikul}"
        users = db.query(User).all()  # Получаем всех пользователей из базы данных
        for user in users:
            await bot.send_message_to_user(user.chat_id, message)
    else:
        message = f"Не удалось обновить данные по артикулу {artikul}"
        users = db.query(User).all()  # Получаем всех пользователей из базы данных
        for user in users:
            await bot.send_message_to_user(user.chat_id, message)

async def start_scheduled_tasks(db: Session):
    products = db.query(Product).all()
    for product in products:
        job_id = f'product_update_{product.artikul}'
        scheduler.add_job(
            update_product_data,
            trigger=IntervalTrigger(minutes=30),
            args=[product.artikul, db],
            id=job_id
        )

@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    await start_scheduled_tasks(db)
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()