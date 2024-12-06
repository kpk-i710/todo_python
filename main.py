from fastapi import FastAPI, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from enum import Enum
from uuid import uuid4
from items import routerAuth


from auth import *

# Настройки приложения
app = FastAPI()

app.include_router(router)
app.include_router(routerAuth)
 