from fastapi import APIRouter, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional

from .crud_blog import create_new_user, check_if_user_exists, login_user, create_new_post, get_post, get_all_posts, \
    update_post, delete_post_data, create_new_comment, delete_comment_data, like_post_func
from .crud_image_analyze import create_new_image, delete_image_data, image_detail_data, update_tag_data, \
    remove_tag_data, update_color, update_size
from .models import User
from . import models, schemas, token
from .database import get_db

router = APIRouter()


# REQUESTS

# Blog
@router.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    # get user data
    user = db.query(models.User).filter(models.User.id == user_id).first()
    check_if_user_exists(user, user_id)
    return user


@router.post("/users/", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # create user
    new_user = create_new_user(user, db)
    return new_user


@router.post("/login/", response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    access_token = login_user(user_credentials, db)
    return schemas.Token(access_token=access_token)


@router.get("/posts/", response_model=List[schemas.PostOut])
def get_posts(search: Optional[str] = "", db: Session = Depends(get_db)):
    results = get_all_posts(db, func, search)
    return results


@router.get("/posts/{post_id}", response_model=schemas.PostOut)
def find_post(post_id: int, db: Session = Depends(get_db)):
    post = get_post(post_id, db, func)
    return post


@router.post("/posts/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db),
                current_user: User = Depends(token.get_current_user)):
    new_post = create_new_post(post, current_user, db)
    return new_post


@router.put("/posts/{post_id}", response_model=schemas.Post)
def update_post_data(post_id: int, post: schemas.PostCreate, db: Session = Depends(get_db),
                     current_user: User = Depends(token.get_current_user)):
    result = update_post(db, post_id, current_user, post)

    return result


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db),
                current_user: User = Depends(token.get_current_user)):
    result = delete_post_data(db, post_id, current_user)
    if result:
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/like_post/", status_code=status.HTTP_201_CREATED)
def like_post_by_id(like_pos_data: schemas.LikePost, db: Session = Depends(get_db),
                    current_user: User = Depends(token.get_current_user)):
    result = like_post_func(db, current_user, like_pos_data)
    return result


@router.post("/new_comment/", status_code=status.HTTP_201_CREATED, response_model=schemas.Comment)
def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db),
                   current_user: User = Depends(token.get_current_user)):
    new_comment = create_new_comment(comment, current_user, db)
    return new_comment


@router.delete("/comment/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, db: Session = Depends(get_db),
                   current_user: User = Depends(token.get_current_user)):
    result = delete_comment_data(db, comment_id)
    if result:
        return Response(status_code=status.HTTP_204_NO_CONTENT)


# ImageAnalyze

@router.post("/upload_image/", status_code=status.HTTP_201_CREATED, response_model=schemas.Images)
def create_image(image: schemas.ImageCreate, db: Session = Depends(get_db)):
    new_image = create_new_image(image, db)
    return new_image


@router.get("/image_detail/{image_id}")
def image_detail(image_id: int, db: Session = Depends(get_db)):
    result = image_detail_data(db, image_id)
    return result


@router.delete("/delete_image/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(image_id: int, db: Session = Depends(get_db)):
    result = delete_image_data(db, image_id)
    if result:
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/update_size/{image_id}")
def update_size_data(image_id: int, sizes: schemas.Sizes, db: Session = Depends(get_db)):
    result = update_size(image_id, sizes, db)
    if result:
        return Response(status_code=status.HTTP_200_OK)


@router.post("/update_color/{image_id}")
def color_image(image_id: int, colors: schemas.Colors, db: Session = Depends(get_db)):
    result = update_color(image_id, colors, db)
    if result:
        return Response(status_code=status.HTTP_200_OK)


@router.post("/update_image_detail/{image_id}", response_model=schemas.Tags)
def update_tag(image_id: int, tag: schemas.Tags, db: Session = Depends(get_db)):
    result = update_tag_data(image_id, tag, db)
    if result:
        return Response(status_code=status.HTTP_200_OK)


@router.post("/remove_image_detail/{image_id}", response_model=schemas.Tags)
def remove_tag(image_id: int, tag: schemas.Tags, db: Session = Depends(get_db)):
    result = remove_tag_data(image_id, tag, db)
    if result:
        return Response(status_code=status.HTTP_200_OK)
