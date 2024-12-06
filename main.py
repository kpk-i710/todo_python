from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import uvicorn
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from model import Data, TokenData, User, UserInDB

SECRET_KEY = "83daa0256a2289b0fb23693bf1f6034d44396675749244721a2b20e896e11662"
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30



# @app.post("/create/")
# async def create(data: Data):
#     return data

# @app.get("/test/{item_id}/")
# async def test(item_id:int,query:int=1):
#     return {"hello": f"world {item_id}"}


pwd_context = CryptContext(schemes=["bcrypt"],)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


app = FastAPI()


def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)


def get_password_hash(password) :
    return pwd_context.hash(password)

def get_user(db,username: str):
    if username in db:
        user_data = db[username]
        return UserInDB(**user_data) 
        
    
def authenticate_user(db,username:str,password: str):
    user = get_user(db,username)
    if not user:
        return False
    if not verify_password(password,user.hashed_password):
        return False
    return user


def create_access_token(data:dict,expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expires = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
        
        
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token:str = Depends(oauth2_scheme)):
    credential_exaption =  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credenitl",headers={"WWW-Authenticate" : "Bearer"})
    
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        token_data  =  TokenData(username=username)
    except JWTError:
        raise credential_exaption
    user = get_user(db,username=token_data.username)
    if user is None:
        raise credential_exaption
    return user