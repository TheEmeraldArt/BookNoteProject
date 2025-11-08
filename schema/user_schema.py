from pydantic import BaseModel, EmailStr



class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    class Config:
        from_attributes = True  # Для работы с SQLAlchemy объектами


class Token(BaseModel):
    access_token: str
    token_type: str