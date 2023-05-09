from fastapi import HTTPException
from starlette import status

from app import models
from app.token import create_access_token
from app.utils import hash_password, verify


def create_new_user(user, db):
    hashed_password = hash_password(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def check_if_user_exists(user, user_id):
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


def login_user(user_credentials, db):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if not verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    access_token = create_access_token(data={"user_id": user.id, "sub": user.email})

    return access_token


def create_new_post(post, current_user, db):
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


def get_post(post_id, db, func):
    post = db.query(models.Post, func.count(models.LikePost.post_id).label("likes")).join(models.LikePost,
                                                                                          models.LikePost.post_id == models.Post.id,
                                                                                          isouter=True).group_by(
        models.Post.id).filter(models.Post.id == post_id).first()

    check_if_exists(post, post_id)

    return post


def check_if_exists(post, post_id):
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


def get_all_posts(db, func, search):
    results = db.query(models.Post, func.count(models.LikePost.post_id).label("likes")).join(models.LikePost,
                                                                                             models.LikePost.post_id == models.Post.id,
                                                                                             isouter=True).group_by(
        models.Post.id).filter(models.Post.title.contains(search)).all()

    return results


def update_post(db, post_id, current_user, post):
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    found_post = post_query.first()

    check_if_exists(found_post, post_id)
    if found_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()


def delete_post_data(db, post_id, current_user):
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    post = post_query.first()

    check_if_exists(post, post_id)

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    post_query.delete(synchronize_session=False)
    db.commit()
    return True


def like_post_func(db, current_user, like_post):
    post = db.query(models.Post).filter(models.Post.id == like_post.post_id).first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    vote_query = db.query(models.LikePost).filter(models.LikePost.post_id == like_post.post_id,
                                                  models.LikePost.user_id == current_user.id)
    found_vote = vote_query.first()
    if like_post.direction == 1:
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)
        new_vote = models.LikePost(post_id=like_post.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "Remove like"}
    else:
        if found_vote is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "Add like"}


def create_new_comment(comment, current_user, db):
    new_comment = models.Comment(user_id=current_user.id, **comment.dict())

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment


def delete_comment_data(db, comment_id):
    comment_query = db.query(models.Comment).filter(models.Comment.id == comment_id)
    comment = comment_query.first()

    check_if_exists(comment, comment_id)
    comment_query.delete(synchronize_session=False)
    db.commit()
    return True
