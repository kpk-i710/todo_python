from fastapi import FastAPI
import uvicorn

app = FastAPI()


if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True)


books = [
    {"id": 1,
     "title": "Асинхронность в Python",
     "author": "Маттью", },
    {"id": 2,
     "title": "Потом в Python",
     "author": "Мак",
     },
]


@app.get('/books')
def read_books():
    return books
