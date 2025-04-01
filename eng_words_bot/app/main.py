from fastapi import FastAPI, Depends, HTTPException, Request, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime

from . import crud, models, schemas, database


app = FastAPI(title="404gram")


app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")


get_db = database.get_db


@app.on_event("startup")
def on_startup():
    print("Creating database tables...")
    database.create_db_and_tables()
    print("Database tables created (if they didn't exist).")


@app.post("/api/users/", response_model=schemas.User)
def create_user_api(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.get("/api/users/{username}", response_model=schemas.User)
def read_user_api(username: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/api/posts/", response_model=schemas.Post)
async def create_post_api(
    username: str = Form(...),
    text_content: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    if not text_content and not image:
        raise HTTPException(status_code=400, detail="Post must have text or an image")

    db_user = crud.get_user_by_username(db, username=username)
    if not db_user:
        print(f"User '{username}' not found, creating...")
        user_data = schemas.UserCreate(username=username)
        db_user = crud.create_user(db=db, user=user_data)

    post_data = schemas.PostCreate(text_content=text_content)
    try:
        return crud.create_post(
            db=db, post_data=post_data, user_id=db_user.id, image=image
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error creating post: {e}")
        raise HTTPException(status_code=500, detail="Could not save post or image")


@app.get("/api/feed/", response_model=List[schemas.Post])
def read_feed_api(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    posts = crud.get_posts_random_feed(db, limit=limit)
    return posts


@app.get("/api/users/{username}/posts/", response_model=List[schemas.Post])
def read_user_posts_api(
    username: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    posts = crud.get_posts_by_user(db=db, user_id=db_user.id, skip=skip, limit=limit)
    return posts


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    """Главная страница - отображает ленту"""
    feed_posts = crud.get_posts_random_feed(db, limit=20)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "posts": feed_posts,
            "page_type": "feed",
            "datetime": datetime,
        },
    )


@app.get("/profile/{username}", response_class=HTMLResponse)
async def read_profile(request: Request, username: str, db: Session = Depends(get_db)):
    """Страница профиля пользователя"""
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_posts = crud.get_posts_by_user(db=db, user_id=db_user.id, limit=20)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "profile_user": db_user,
            "posts": user_posts,
            "page_type": "profile",
            "datetime": datetime,
        },
    )
