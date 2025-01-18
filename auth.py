from fastapi import FastAPI, HTTPException, Depends ,APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
# Настройки безопасности
SECRET_KEY = "supersecretkey"  # Замените на свой секретный ключ
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

users_db = {
    "admin@example.com": {
        "email": "admin@example.com",
        "hashed_password": pwd_context.hash("adminpass"),
        "role": "admin"
    },
    "brigadier@example.com": {
        "email": "brigadier@example.com",
        "hashed_password": pwd_context.hash("brigadierpass"),
        "role": "brigadier"
    },
    "user@example.com": {
        "email": "user@example.com",
        "hashed_password": pwd_context.hash("userpass"),
        "role": "user"
    },
}

# Инициализация маршрутизатора
router = APIRouter()


class LoginForm(BaseModel):
    username: str
    password: str

# Эндпоинт регистрации
@router.post("/register")
async def register(email: str, password: str):
    if email in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = get_password_hash(password)
    users_db[email] = {"email": email, "hashed_password": hashed_password}
    return {"message": "User registered successfully"}

# Эндпоинт авторизации
@router.post("/token")
async def login(form_data: LoginForm):
    user = users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Пример защищенного эндпоинта
@router.get("/protected")
async def protected(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None or email not in users_db:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"message": "Access granted", "email": email}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")



# Утилиты
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)