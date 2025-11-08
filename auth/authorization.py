import os

from sqlalchemy import select

from passlib.context import CryptContext

from jose import JWTError, jwt

from datetime import datetime, timedelta

from fastapi import  HTTPException, status

from sqlalchemy.ext.asyncio import  AsyncSession

from typing import  Optional

from database.users_db import UserModel




# Настройки для JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Настройка хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Хэширует пароль"""
    return pwd_context.hash(password)



def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль против хэша"""
    return pwd_context.verify(plain_password,hashed_password)



def create_access_token(data: dict) -> str:
    """Создает JWT токен"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



async def get_user_by_username(session: AsyncSession, username: str) -> Optional[UserModel]:
    """Находит пользователя по username"""
    result = await session.execute(select(UserModel).where(UserModel.username == username))
    return result.scalar_one_or_none()



async def get_user_by_email(session: AsyncSession, email: str) -> Optional[UserModel]:
    """Находит пользователя по email"""
    result = await session.execute(select(UserModel).where(UserModel.email == email))
    return result.scalar_one_or_none()



async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[UserModel]:
    """Находит пользователя по id"""
    result = await session.execute(select(UserModel).where(UserModel.id == user_id))
    return result.scalar_one_or_none()



async def authenticate_user(session: AsyncSession, username: str, password: str) -> Optional[UserModel]:
    """Аутентифицирует пользователя"""
    user = await get_user_by_username(session, username)
    if not user or not verify_password(password, user.password):
        return None
    return user



async def get_current_user_from_token(
        token: str,
        session: AsyncSession
) -> UserModel:
    """Получает пользователя из JWT токена"""
    credentials_exception = HTTPException(
        status_code= status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials",
        headers = {"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms= [ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_username(session, username)
    if user is None:
        raise credentials_exception
    return user