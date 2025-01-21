# import httpx
# from sqlalchemy.orm import Session
#
# from models import Product, User
# import json
#
#
# async def fetch_wb_data(artikul: int):
#     url = f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={artikul}"
#     async with httpx.AsyncClient() as client:
#         response = await client.get(url)
#         response.raise_for_status()
#         data = response.json()
#         return data
#
#
# def process_wb_data(data: dict):
#         if 'data' in data and 'products' in data['data']:
#             product = data['data']['products'][0]
#
#             name = product.get("name")
#             artikul = product.get("id")
#             price = product.get("salePriceU")/100
#             rating = product.get("rating")
#             total_stock = sum(stock['qty'] for stock in product.get('sizes')[0].get("stocks")) if product.get('sizes') else 0
#
#             return {
#                 "name": name,
#                 "artikul": artikul,
#                 "price": price,
#                 "rating": rating,
#                 "total_stock": total_stock
#             }
#         return None
#
#
#
# def save_product_to_db(db: Session, data: dict):
#     product = db.query(Product).filter(Product.artikul == data['artikul']).first()
#     if not product:
#         product = Product(
#             artikul=data['artikul'],
#             name=data['name'],
#             price=data['price'],
#             rating=data['rating'],
#             total_stock=data['total_stock']
#         )
#         db.add(product)
#     else:
#         product.name = data['name']
#         product.price = data['price']
#         product.rating = data['rating']
#         product.total_stock = data['total_stock']
#     db.commit()
#     db.refresh(product)
#     return product
#
# def update_product(db: Session, artikul: int):
#     product = db.query(Product).filter(Product.artikul == artikul).first()
#     if product:
#         # Здесь можно добавить логику обновления данных товара
#         db.commit()
#         db.refresh(product)
#     return product
#
# def get_all_users(db: Session):
#     return db.query(User).all()
#
#
#
#
# async def update_product(db: Session, artikul: int):
#     data = await fetch_wb_data(artikul)
#     product_data = process_wb_data(data)
#
#     if not product_data:
#         return None
#
#     db_product = db.query(Product).filter(Product.artikul == artikul).first()
#     if db_product:
#         db_product.name = product_data['name']
#         db_product.price = product_data['price']
#         db_product.rating = product_data['rating']
#         db_product.total_stock = product_data['total_stock']
#         db.commit()
#         db.refresh(db_product)
#     else:
#          db_product = Product(
#         name = product_data['name'],
#         artikul = product_data['artikul'],
#         price = product_data['price'],
#         rating = product_data['rating'],
#         total_stock = product_data['total_stock']
#         )
#          db.add(db_product)
#          db.commit()
#          db.refresh(db_product)
#
#     return db_product


import httpx
from sqlalchemy.orm import Session
from models import Product
import logging

logger = logging.getLogger(__name__)

async def fetch_wb_data(artikul: int):
    url = f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={artikul}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

def process_wb_data(data: dict):
    if not data or 'data' not in data or 'products' not in data['data'] or not data['data']['products']:
        return None

    product = data['data']['products'][0]

    name = product.get("name")
    artikul = product.get("id")
    price = product.get("salePriceU", 0) / 100  # Добавим значение по умолчанию
    rating = product.get("rating", 0)  # Добавим значение по умолчанию
    total_stock = sum(stock['qty'] for stock in product.get('sizes')[0].get("stocks")) if product.get('sizes') else 0

    return {
        "name": name,
        "artikul": artikul,
        "price": price,
        "rating": rating,
        "total_stock": total_stock
    }

def save_product_to_db(db: Session, data: dict):
    if not data or 'artikul' not in data:
        raise ValueError("Ключ 'artikul' отсутствует в данных")

    product = db.query(Product).filter(Product.artikul == data['artikul']).first()
    if product:
        # Обновляем существующий продукт
        product.name = data.get('name', product.name)
        product.price = data.get('price', product.price)
        product.rating = data.get('rating', product.rating)
        product.total_stock = data.get('total_stock', product.total_stock)
    else:
        # Создаем новый продукт
        product = Product(
            artikul=data['artikul'],
            name=data.get('name'),
            price=data.get('price'),
            rating=data.get('rating'),
            total_stock=data.get('total_stock')
        )
        db.add(product)
    db.commit()
    db.refresh(product)
    return product

async def update_product(db: Session, artikul: int):
    data = await fetch_wb_data(artikul)
    product_data = process_wb_data(data)

    if not product_data:
        logger.error(f"Данные для артикула {artikul} не найдены")
        return None

    db_product = db.query(Product).filter(Product.artikul == artikul).first()
    if db_product:
        db_product.name = product_data['name']
        db_product.price = product_data['price']
        db_product.rating = product_data['rating']
        db_product.total_stock = product_data['total_stock']
        db.commit()
        db.refresh(db_product)
    else:
        db_product = Product(
            name=product_data['name'],
            artikul=product_data['artikul'],
            price=product_data['price'],
            rating=product_data['rating'],
            total_stock=product_data['total_stock']
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)

    return db_product