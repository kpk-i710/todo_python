from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

from auth import *

# Настройки приложения
app = FastAPI()

# Модели и хранилище
users_db = {}  # Временное хранилище пользователей

# Эндпоинт регистрации
@app.post("/register")
async def register(email: str, password: str):
    if email in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = get_password_hash(password)
    users_db[email] = {"email": email, "hashed_password": hashed_password}
    return {"message": "User registered successfully"}

# Эндпоинт авторизации
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Пример защищенного эндпоинта
@app.get("/protected")
async def protected(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None or email not in users_db:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"message": "Access granted", "email": email}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
