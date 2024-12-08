from fastapi import APIRouter, HTTPException, Depends
from jose import JWTError
import jwt
from pydantic import BaseModel
from typing import List, Optional
from auth import get_password_hash, verify_password, users_db, SECRET_KEY, ALGORITHM, oauth2_scheme, create_access_token
import uuid
from passlib.context import CryptContext
 
# Инициализация маршрутизатора
routerAuth = APIRouter()


# Модели данных
class Product(BaseModel):
    id: int
    title: str
    description: str


class Comment(BaseModel):
    product_id: int
    user_email: str
    content: str


class User(BaseModel):
    email: str
    role: str


# База данных в памяти
products_db = [
    {"id": 1, "title": "Товар 1", "description": "Описание товара 1"},
    {"id": 2, "title": "Товар 2", "description": "Описание товара 2"},
]
comments_db = [
    {
        "product_id": 1,
        "user_email": "user@example.com",
        "content": "Это отличный товар!",
        "parent_id": None,  # Это корневой комментарий
    }
]

users_db = {
    "admin@example.com": {
        "email": "admin@example.com",
        "hashed_password": CryptContext(schemes=["bcrypt"]).hash("adminpass"),
        "role": "admin",
    },
    "brigadier@example.com": {
        "email": "brigadier@example.com",
        "hashed_password": CryptContext(schemes=["bcrypt"]).hash("brigadierpass"),
        "role": "brigadier",
    },
    "user@example.com": {
        "email": "user@example.com",
        "hashed_password": CryptContext(schemes=["bcrypt"]).hash("userpass"),
        "role": "user",
    },
}


# Функции для работы с пользователями
def get_user(email: str) -> Optional[dict]:
    return users_db.get(email)


# Эндпоинты для работы с товарами
@routerAuth.get("/products", response_model=List[Product])
def get_products():
    return products_db


@routerAuth.post("/products", response_model=Product)
def create_product(product: Product):
    if any(p["id"] == product.id for p in products_db):
        raise HTTPException(status_code=400, detail="Товар с таким ID уже существует")
    products_db.append(product.dict())
    return product


@routerAuth.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    for product in products_db:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Товар не найден")


# Эндпоинты для работы с комментариями
@routerAuth.get("/products/{product_id}/comments", response_model=List[Comment])
def get_comments(product_id: int):
    return [comment for comment in comments_db if comment["product_id"] == product_id]


@routerAuth.post("/products/{product_id}/comments", response_model=Comment)
def add_comment(product_id: int, comment: Comment):
    if not any(p["id"] == product_id for p in products_db):
        raise HTTPException(status_code=404, detail="Товар не найден")
    comments_db.append(comment.dict())
    return comment
 