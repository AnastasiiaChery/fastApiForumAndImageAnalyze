from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from pydantic.types import conint


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PostBase(BaseModel):
    title: str
    content: str
    image: str


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: User

    class Config:
        orm_mode = True


class PostOut(BaseModel):
    Post: Post
    likes: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    id: Optional[str]
    username: Optional[str]


class LikePost(BaseModel):
    post_id: int
    direction: conint(le=1)


class CommentBase(BaseModel):
    comment: str
    post_id: int


class CommentCreate(CommentBase):
    pass


class Comment(CommentBase):
    id: int
    user_id: int
    post_id: int

    class Config:
        orm_mode = True


class ImageBase(BaseModel):
    image: str


class Images(ImageBase):
    id: int

    class Config:
        orm_mode = True


class ImageCreate(ImageBase):
    pass


class ImageDetail(BaseModel):
    tags: dict


class Tags(BaseModel):
    tag_name: str
    tag_data: str


class Colors(BaseModel):
    color_code: str


class Sizes(BaseModel):
    left: Optional[int]
    upper: Optional[int]
    right: Optional[int]
    lower: Optional[int]
    width: Optional[int]
    height: Optional[int]
