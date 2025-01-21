# from sqlalchemy import create_engine, Column, Integer, String, Float
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
#
# from dotenv import load_dotenv
# import os
#
#
# load_dotenv()
#
#
# DATABASE_URL = os.getenv("DATABASE_URL")
#
#
# engine = create_engine(DATABASE_URL)
# Base = declarative_base()
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# class Product(Base):
#     __tablename__ = "products"
#
#     id = Column(Integer, primary_key=True, index=True)
#     artikul = Column(Integer, unique=True, index=True)
#     name = Column(String)
#     price = Column(Float)
#     rating = Column(Float)
#     total_stock = Column(Integer)
#
#
# Base.metadata.create_all(bind=engine)
#
#
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    artikul = Column(Integer, unique=True, index=True)
    name = Column(String)
    price = Column(Float)
    rating = Column(Float)
    total_stock = Column(Integer)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, unique=True, index=True)  # Уникальный chat_id пользователя

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()