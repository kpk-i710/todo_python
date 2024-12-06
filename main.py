from fastapi import FastAPI


from auth import *

# Настройки приложения
app = FastAPI()

app.include_router(router)