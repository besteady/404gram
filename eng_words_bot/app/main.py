# app/main.py
from fastapi import FastAPI, Depends, HTTPException, Request, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime # для crud.create_post

from . import crud, models, schemas, database

# Создаем таблицы при первом запуске (в реальном приложении лучше использовать Alembic)
# database.create_db_and_tables()
# Вызывать вручную или при запуске приложения:
# import app.database
# app.database.create_db_and_tables()

app = FastAPI(title="404gram")

# Монтируем статические файлы (CSS, JS, Images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Настраиваем шаблоны Jinja2
templates = Jinja2Templates(directory="templates")

# --- Зависимости ---
get_db = database.get_db

# --- Обработчики событий приложения ---
@app.on_event("startup")
def on_startup():
    print("Creating database tables...")
    database.create_db_and_tables()
    print("Database tables created (if they didn't exist).")


# --- API Эндпоинты ---

# Создание пользователя (упрощенное)
@app.post("/api/users/", response_model=schemas.User)
def create_user_api(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

# Получение информации о пользователе
@app.get("/api/users/{username}", response_model=schemas.User)
def read_user_api(username: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Создание поста
@app.post("/api/posts/", response_model=schemas.Post)
async def create_post_api(
    username: str = Form(...), # Имя пользователя, создающего пост
    text_content: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    if not text_content and not image:
        raise HTTPException(status_code=400, detail="Post must have text or an image")

    db_user = crud.get_user_by_username(db, username=username)
    if not db_user:
         # Если пользователя нет, создадим его (для упрощения)
         # В реальном приложении нужна аутентификация!
         print(f"User '{username}' not found, creating...")
         user_data = schemas.UserCreate(username=username)
         db_user = crud.create_user(db=db, user=user_data)
         # raise HTTPException(status_code=404, detail=f"User '{username}' not found")

    post_data = schemas.PostCreate(text_content=text_content)
    try:
        return crud.create_post(db=db, post_data=post_data, user_id=db_user.id, image=image)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Логирование ошибки было бы полезно здесь
        print(f"Error creating post: {e}")
        raise HTTPException(status_code=500, detail="Could not save post or image")


# Получение ленты случайных постов
@app.get("/api/feed/", response_model=List[schemas.Post])
def read_feed_api(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    posts = crud.get_posts_random_feed(db, limit=limit)
    return posts

# Получение постов конкретного пользователя
@app.get("/api/users/{username}/posts/", response_model=List[schemas.Post])
def read_user_posts_api(username: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    posts = crud.get_posts_by_user(db=db, user_id=db_user.id, skip=skip, limit=limit)
    return posts


# --- HTML Страницы ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    """Главная страница - отображает ленту"""
    feed_posts = crud.get_posts_random_feed(db, limit=20) # Получаем посты для ленты
    # print(f"Feed posts: {feed_posts}") # Для отладки
    return templates.TemplateResponse("index.html", {"request": request, "posts": feed_posts, "page_type": "feed",
                                                     "datetime": datetime})
@app.get("/profile/{username}", response_class=HTMLResponse)
async def read_profile(request: Request, username: str, db: Session = Depends(get_db)):
    """Страница профиля пользователя"""
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        # Можно вернуть 404 или редирект на главную с сообщением
        # return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
         raise HTTPException(status_code=404, detail="User not found") # Или так

    user_posts = crud.get_posts_by_user(db=db, user_id=db_user.id, limit=20)
    return templates.TemplateResponse("index.html", {"request": request, "profile_user": db_user, "posts": user_posts,
                                                     "page_type": "profile", "datetime": datetime})
# Обработка формы создания поста (если отправлять не через JS API)
# @app.post("/create-post-form/", response_class=RedirectResponse)
# async def handle_create_post_form(
#     request: Request,
#     username: str = Form(...),
#     text_content: Optional[str] = Form(None),
#     image: Optional[UploadFile] = File(None),
#     db: Session = Depends(get_db)
# ):
#     # Этот код дублирует /api/posts/, лучше использовать JS для отправки на API
#     # Но оставлю как пример обработки формы с редиректом
#     if not text_content and not image:
#         # Вернуть на главную с ошибкой? Сложно без сессий/куки.
#         # Проще валидировать на фронте или через API
#         return RedirectResponse("/", status_code=303) # See Other

#     db_user = crud.get_user_by_username(db, username=username)
#     if not db_user:
#         user_data = schemas.UserCreate(username=username)
#         db_user = crud.create_user(db=db, user=user_data)

#     post_data = schemas.PostCreate(text_content=text_content)
#     try:
#         crud.create_post(db=db, post_data=post_data, user_id=db_user.id, image=image)
#     except ValueError as e:
#          # Обработка ошибки - как передать сообщение пользователю?
#          print(f"Form Error: {e}")
#          return RedirectResponse("/", status_code=303)
#     except Exception as e:
#         print(f"Form Error creating post: {e}")
#         return RedirectResponse("/", status_code=303)

#     # Редирект на профиль пользователя после успешного поста
#     return RedirectResponse(f"/profile/{username}", status_code=303) # See Other