from fastapi import HTTPException
from starlette import status

from app import models
from app.token import create_access_token
from app.utils import hash_password, verify


def create_new_user(user, db):
    """
    Create a new user and store it in the database.

    Args:
        user (UserCreate): User creation data.
        db (Database): Database session.

    Returns:
        User: The newly created user object.
    """
    hashed_password = hash_password(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def check_if_user_exists(user):
    """
    Check if the user exists. If not, raise a 404 Not Found exception.

    Args:
        user: User object or None.

    Raises:
        HTTPException: If the user does not exist.
    """
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


def login_user(user_credentials, db):
    """
    Log in the user and generate an access token.

    Args:
        user_credentials (UserCredentials): User credentials for login.
        db (Database): Database session.

    Returns:
        str: Access token for the logged-in user.

    Raises:
        HTTPException: If the user does not exist or the password is incorrect.
    """
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if not verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    access_token = create_access_token(data={"user_id": user.id, "sub": user.email})

    return access_token


def create_new_post(post, current_user, db):
    """
    Create a new post and store it in the database.

    Args:
        post (PostCreate): Post creation data.
        current_user (User): Currently logged-in user.
        db (Database): Database session.

    Returns:
        Post: The newly created post object.
    """
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


def get_post(post_id, db, func):
    """
    Retrieve a post by its ID.

    Args:
        post_id: ID of the post to retrieve.
        db (Database): Database session.
        func: Database function for aggregation.

    Returns:
        Post: The retrieved post.

    Raises:
        HTTPException: If the post does not exist.
    """
    post = db.query(models.Post, func.count(models.LikePost.post_id).label("likes")).join(models.LikePost,
                                                                                          models.LikePost.post_id == models.Post.id,
                                                                                          isouter=True).group_by(
        models.Post.id).filter(models.Post.id == post_id).first()

    check_if_exists(post, post_id)

    return post


def check_if_exists(post):
    """
    Check if the post exists. If not, raise a 404 Not Found exception.

    Args:
        post: Post object or None.

    Raises:
        HTTPException: If the post does not
    """
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


def get_all_posts(db, func, search):
    """
    Get all posts that match the search criteria.

    Args:
        db (Database): Database session.
        func: Database function for aggregation.
        search (str): Search keyword for filtering posts.

    Returns:
        List: List of post objects matching the search criteria.
    """
    results = db.query(models.Post, func.count(models.LikePost.post_id).label("likes")).join(models.LikePost,
                                                                                             models.LikePost.post_id == models.Post.id,
                                                                                             isouter=True).group_by(
        models.Post.id).filter(models.Post.title.contains(search)).all()

    return results


def update_post(db, post_id, current_user, post):
    """
    Update a post with new data.

    Args:
        db (Database): Database session.
        post_id: ID of the post to update.
        current_user (User): Currently logged-in user.
        post (PostUpdate): Updated post data.

    Returns:
        Post: The updated post object.

    Raises:
        HTTPException: If the post does not exist or the user is not the owner.
    """
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    found_post = post_query.first()

    check_if_exists(found_post, post_id)
    if found_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()


def delete_post_data(db, post_id, current_user):
    """
    Delete a post.

    Args:
        db (Database): Database session.
        post_id: ID of the post to delete.
        current_user (User): Currently logged-in user.

    Returns:
        bool: True if the post is deleted successfully.

    Raises:
        HTTPException: If the post does not exist or the user is not the owner.
    """
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    post = post_query.first()

    check_if_exists(post, post_id)

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    post_query.delete(synchronize_session=False)
    db.commit()
    return True


def like_post_func(db, current_user, like_post):
    """
    Like or unlike a post.

    Args:
        db (Database): Database session.
        current_user (User): Currently logged-in user.
        like_post (LikePost): Like or unlike data.

    Returns:
        dict: Success message.

    Raises:
        HTTPException: If the post does not exist or there is a conflict in the vote.
    """
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
    """
    Create a new comment.

    Args:
        comment (CommentCreate): Comment data.
        current_user (User): Currently logged-in user.
        db (Database): Database session.

    Returns:
        Comment: The created comment object.
    """
    new_comment = models.Comment(user_id=current_user.id, **comment.dict())

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment


def delete_comment_data(db, comment_id):
    """
    Delete a comment.

    Args:
        db (Database): Database session.
        comment_id: ID of the comment to delete.

    Returns:
        bool: True if the comment is deleted successfully.

    Raises:
        HTTPException: If the comment does not exist.
    """
    comment_query = db.query(models.Comment).filter(models.Comment.id == comment_id)
    comment = comment_query.first()

    check_if_exists(comment, comment_id)
    comment_query.delete(synchronize_session=False)
    db.commit()
    return True
