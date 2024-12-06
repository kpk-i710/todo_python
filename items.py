from fastapi import APIRouter, HTTPException, Depends
from jose import JWTError
import jwt
from pydantic import BaseModel
from typing import List, Optional
from auth import get_password_hash, verify_password, users_db, SECRET_KEY, ALGORITHM, oauth2_scheme, create_access_token
import uuid

# Структура данных товара
class Item(BaseModel):
    name: str
    description: str
    price: float

# Структура данных комментария
class Comment(BaseModel):
    user_email: str
    content: str
    reply_to: Optional[str] = None  # Ответ на комментарий (если есть)

# Инициализация маршрутизатора
routerAuth = APIRouter()

# Список товаров и комментариев (можно заменить на реальную БД)
items_db = {}
comments_db = {}

# Эндпоинт для добавления товара
@routerAuth.post("/items/")
async def create_item(item: Item, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None or email not in users_db:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        item_id = str(uuid.uuid4())  # Генерируем уникальный ID для товара
        items_db[item_id] = item
        
        return {"message": "Item created successfully", "item_id": item_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Эндпоинт для получения списка товаров
@routerAuth.get("/items/", response_model=List[Item])
async def get_items():
    return list(items_db.values())

# Эндпоинт для добавления комментария
@routerAuth.post("/comments/{item_id}/")
async def add_comment(item_id: str, comment: Comment, token: str = Depends(oauth2_scheme)):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None or email not in users_db:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        comment_id = str(uuid.uuid4())  # Генерируем уникальный ID для комментария
        comment_data = comment.dict()
        comment_data["user_email"] = email
        comments_db.setdefault(item_id, []).append(comment_data)
        
        return {"message": "Comment added successfully", "comment_id": comment_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Эндпоинт для получения комментариев к товару
@routerAuth.get("/comments/{item_id}/", response_model=List[Comment])
async def get_comments(item_id: str):
    if item_id not in comments_db:
        raise HTTPException(status_code=404, detail="No comments found")
    return comments_db[item_id]

# Эндпоинт для ответа на комментарий
@routerAuth.post("/comments/reply/{item_id}/{comment_id}/")
async def reply_to_comment(item_id: str, comment_id: str, reply_content: str, token: str = Depends(oauth2_scheme)):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if item_id not in comments_db or comment_id not in [comment["id"] for comment in comments_db[item_id]]:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        user_role = users_db[email]["role"]
        
        # Проверка роли (только админ или бригадир могут отвечать)
        if user_role not in ["admin", "brigadier"]:
            raise HTTPException(status_code=403, detail="You do not have permission to reply")
        
        # Находим комментарий и добавляем ответ
        for comment in comments_db[item_id]:
            if comment["id"] == comment_id:
                comment["reply"] = reply_content
                break
        
        return {"message": "Reply added successfully"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
