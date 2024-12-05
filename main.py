from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel

app = FastAPI()

books = [
    {"id": 1,
     "title": "Асинхронность в Python",
     "author": "Маттью", },
    {"id": 2,
     "title": "Потом в Python",
     "author": "Мак1",
     },
]


@app.get('/books', tags=['Книги1'], summary="Все книги")
def read_books():
    return books


@app.get('/books/{book_id}', tags=['Книги1'], summary="Получит одну книгу")
def get_book(book_id: int):
    for book in books:
        if book['id'] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Книга не найдена")


class NewBook(BaseModel):
    title: str
    author: str


@app.post('/books',summary='Создать книгу')
def create_book(new_book: NewBook):
    books.append({
        "id": len(books)+1,
        "title": new_book.title,
        "author": new_book.author,
    })
    return {"success":True,"message": "Книга успешно добавлена"}
