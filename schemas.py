from pydantic import BaseModel, EmailStr, constr, Field
from typing import List


class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: EmailStr | None = None


class PostCreate(BaseModel):
    text: constr(max_length=1048576)  # 1 MB size limit


class PostOut(BaseModel):
    id: int
    text: str
    owner_id: int

    class Config:
        orm_mode = True
