
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import models
import schemas
import database
import auth
import utils

app = FastAPI()


@app.post("/signup", response_model=schemas.UserOut)
def signup(user: schemas.UserCreate, db: Session = Depends(database.SessionLocal)):
    db_user = auth.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.SessionLocal)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect email or password")
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/addpost", response_model=schemas.PostOut)
def add_post(post: schemas.PostCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.SessionLocal)):
    db_post = models.Post(text=post.text, owner_id=current_user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@app.get("/getposts", response_model=List[schemas.PostOut])
def get_posts(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.SessionLocal)):
    cached_posts = utils.cache_get(current_user.id)
    if cached_posts:
        return cached_posts
    posts = db.query(models.Post).filter(
        models.Post.owner_id == current_user.id).all()
    utils.cache_set(current_user.id, posts)
    return posts


@app.delete("/deletepost/{post_id}", response_model=schemas.PostOut)
def delete_post(post_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.SessionLocal)):
    post = db.query(models.Post).filter(models.Post.id == post_id,
                                        models.Post.owner_id == current_user.id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()
    return post
