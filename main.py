# from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
# from sqlalchemy.orm import Session
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from apscheduler.triggers.interval import IntervalTrigger
# from typing import Dict
# from sqlalchemy import select
#
# from models import get_db, Product
# import services
# import bot
# from database import init_db
# from pydantic import BaseModel
#
# import logging
#
# app = FastAPI()
# init_db()
#
# scheduler = AsyncIOScheduler()
#
#
# class ProductArtikul(BaseModel):
#     artikul: int
#
#
# async def process_product_data(artikul: int, db: Session):
#     data = await services.fetch_wb_data(artikul)
#     db_product = services.save_product_to_db(db, data)
#
#     if db_product:
#         message = f"Данные по товару {artikul} обновлены"
#         chat_id = 1168986339  # Замените на фактический ID чата
#         await bot.send_message_to_user(chat_id, message)
#     else:
#         message = f"Не удалось обновить данные по товару {artikul}"
#         chat_id = 1168986339  # Замените на фактический ID чата
#         await bot.send_message_to_user(chat_id, message)
#
#
# @app.post("/api/v1/products")
# async def create_product_data(product: ProductArtikul, background_tasks: BackgroundTasks,
#                               db: Session = Depends(get_db)):
#     background_tasks.add_task(process_product_data, product.artikul, db)
#     return {"message": "Сбор данных запущен"}
#
#
# @app.get("/api/v1/subscribe/{artikul}")
# async def subscribe_to_product(artikul: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
#     job_id = f'product_update_{artikul}'
#     if scheduler.get_job(job_id):
#         raise HTTPException(status_code=400, detail="Уже подписан на этот артикул")
#
#     background_tasks.add_task(start_periodic_update, artikul, job_id, db)
#     return {"message": f"Подписаны на артикул {artikul}"}
#
#
# async def start_periodic_update(artikul: int, job_id: str, db: Session):
#     scheduler.add_job(
#         update_product_data,
#         trigger=IntervalTrigger(minutes=30),
#         args=[artikul, db],
#         id=job_id
#     )
#
#
# async def update_product_data(artikul: int, db: Session):
#     db_product = await services.update_product(db, artikul)
#     if db_product:
#         message = f"Обновлены данные по артикулу {artikul}"
#         chat_id = 838440289  # Замените на фактический ID чата
#         await bot.send_message_to_user(chat_id, message)
#     else:
#         message = f"Не удалось обновить данные по артикулу {artikul}"
#         chat_id = 838440289  # Замените на фактический ID чата
#         await bot.send_message_to_user(chat_id, message)
#
#
# async def start_scheduled_tasks(db: Session):
#     products = db.execute(select(Product)).scalars().all()
#     for product in products:
#         job_id = f'product_update_{product.artikul}'
#         scheduler.add_job(
#             update_product_data,
#             trigger=IntervalTrigger(minutes=30),
#             args=[product.artikul, db],
#             id=job_id
#         )
#
#
# @app.on_event("startup")
# async def startup_event():
#     db = next(get_db())
#     await start_scheduled_tasks(db)
#     scheduler.start()
#
#
# @app.on_event("shutdown")
# async def shutdown_event():
#     scheduler.shutdown()



from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from typing import Dict
from sqlalchemy import select

from models import get_db, Product, User
import services
import bot
from database import init_db
from pydantic import BaseModel

import logging

app = FastAPI()
init_db()

scheduler = AsyncIOScheduler()

class ProductArtikul(BaseModel):
    artikul: int

async def process_product_data(artikul: int, db: Session):
    data = await services.fetch_wb_data(artikul)
    db_product = services.save_product_to_db(db, data)

    if db_product:
        message = f"Данные по товару {artikul} обновлены"
        users = services.get_all_users(db)
        for user in users:
            await bot.send_message_to_user(user.chat_id, message)
    else:
        message = f"Не удалось обновить данные по товару {artikul}"
        users = services.get_all_users(db)
        for user in users:
            await bot.send_message_to_user(user.chat_id, message)

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
        users = services.get_all_users(db)
        for user in users:
            await bot.send_message_to_user(user.chat_id, message)
    else:
        message = f"Не удалось обновить данные по артикулу {artikul}"
        users = services.get_all_users(db)
        for user in users:
            await bot.send_message_to_user(user.chat_id, message)

async def start_scheduled_tasks(db: Session):
    products = db.execute(select(Product)).scalars().all()
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