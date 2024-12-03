from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import  BaseModel

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


@app.get('/books',tags=['Книги1'],summary="Все книги")
def read_books():
    return books

@app.get('/books/{book_id}',tags=['Книги1'],summary="Получит одну книгу")
def get_book(book_id:int):
    for book in books:
        if book['id'] == book_id:
            return book
    raise HTTPException(status_code=404,detail="Книга не найдена")


@app.post('books')
def create_book():
