from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class Books(BaseModel):
    title: str
    author: str
    year: int
    genre: str

books = {
    1: {"title": "Book One", "author": "Author A", "year": 2021, "genre": "Fiction"},
    2: {"title": "Book Two", "author": "Author B", "year": 2020, "genre": "Non-Fiction"},
}

@app.get("/")
async def get_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/add_a_book/", response_class=HTMLResponse)
async def get_add_a_book(request: Request):
    return templates.TemplateResponse("add_a_book.html", {"request": request, "books": books})

@app.post("/add_a_book/")
async def add_a_book(request: Request, title: str = Form(...), author: str = Form(...),
                     year: str = Form(...), genre: str = Form(...)):
    if not year.isdigit():
        return templates.TemplateResponse("error.html", {"request": request, "message": "Год должен быть числом!"})
    year = int(year)
    if any(book["title"] == title for book in books.values()):
        return templates.TemplateResponse("error.html", {"request": request, "message": "Книга с таким названием уже существует!"})

    book_id = max(books.keys()) + 1
    books[book_id] = {"title": title, "author": author, "year": year, "genre": genre}
    return templates.TemplateResponse("add_a_book.html", {"request": request, "books": books})

@app.get("/show_books/", response_class=HTMLResponse)
async def show_books(request: Request):
    if not books:
        return templates.TemplateResponse("error.html", {"request": request, "message": "Список книг пуст!"})
    return templates.TemplateResponse("show_books.html", {"request": request, "books": books})

@app.get("/edit_a_book/{book_id}", response_class=HTMLResponse)
async def edit_a_book_view(book_id: int, request: Request):
    if book_id not in books:
        return templates.TemplateResponse("error.html", {"request": request, "message": "Книга не найдена!"})
    return templates.TemplateResponse("edit_a_book.html", {"request": request, "book": books[book_id], "book_id": book_id})

@app.post("/edit_a_book/{book_id}", response_class=HTMLResponse)
async def edit_a_book(request: Request, book_id: int, title: str = Form(...), 
                      author: str = Form(...), year: str = Form(...), 
                      genre: str = Form(...)):
    if not year.isdigit():
        return templates.TemplateResponse("error.html", {"request": request, "message": "Год должен быть числом!"})
    year = int(year)
    if book_id in books:
        books[book_id] = {
            "title": title,
            "author": author,
            "year": year,
            "genre": genre
        }
        return templates.TemplateResponse("book_saved.html", {"request": request, "message": "Книга успешно обновлена!"})
    return templates.TemplateResponse("error.html", {"request": request, "message": "Книга не найдена!"})

@app.get("/book_saved", response_class=HTMLResponse)
async def book_saved(request: Request):
    return templates.TemplateResponse("book_saved.html", {"request": request})

@app.get("/select_book/", response_class=HTMLResponse)
async def select_books(request: Request):
    return templates.TemplateResponse("select_book.html", {"request": request, "books": books})

@app.delete("/delete_a_book/{book_id}", response_class=HTMLResponse)
async def delete_a_book(request: Request, book_id: int):
    if book_id in books:
        del books[book_id]
        return templates.TemplateResponse("delete_a_book.html", {"request": request, "message": "Книга удалена успешно!"})
    else:
        return templates.TemplateResponse("error.html", {"request": request, "message": "Книга не найдена!"})
    
    
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)