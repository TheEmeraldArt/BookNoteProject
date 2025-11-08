from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

from fastapi import HTTPException, status

from loguru import logger

from database.users_db import UserModel

from schema.user_schema import UserSchema

from auth.authorization import get_user_by_username, get_password_hash

from typing import  Optional




class UsersCRUD:
    """CRUD операции для работы с пользователями"""


    async def create_user(
            self,
            session: AsyncSession,
            user_data: UserSchema
            ) -> UserModel:
        
        """Создает нового пользователя"""
        # Проверяем, нет ли уже такого пользователя
        if await get_user_by_username(session, user_data.username):
            raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail = "Username already registered"
            )
        if await get_user_by_username(session, user_data.email):
            raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail = "Email already registered"
            )
        # Хэшируем пароль
        hashed_password = get_password_hash(user_data.password)
        try:
            logger.info("create_user: запрос на создание нового пользователя успешен")
            # Создаем пользователя
            user = UserModel(
            username = user_data.username,
            email = user_data.email,
            password = hashed_password,
            role="user"
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            logger.info("create_user: запрос на создание нового пользователя выполнен")
            return user
        except Exception as e:
            logger.error("create_user: пользователь не создан")
            raise HTTPException(status_code = 400, detail = f"пользователь {e} не создан: ошибка")



    async def read_all_users(
            self,
            session: AsyncSession,
            )-> list[UserModel]:
        try:
            logger.info("Users.read_all_users: считывание всех пользователей")
            
            query = select(UserModel)
            result = await session.execute(query)
            users = result.scalars().all()
            logger.info("Users.read_all_users: считывание всех пользователей выполнено")
            return users
        except Exception as e:
            logger.error(f"read_all_users: считывание всех пользователей {e} не выполнено")



    async def read_user_by_id(
            self,
            session: AsyncSession,
            user_id: UserSchema
            ) -> UserModel:
        try:
            logger.info(f"read_user_by_id: считывание пользователя по id {user_id}")

            query = select(UserModel).where(UserModel.id == user_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                logger.warning(f"Users.read_user_by_id: Пользователь с ID {user_id} не найден")
                raise HTTPException(status_code=500, detail = f"Пользователь не найден")
            return user
        except Exception as e:
            logger.error(f"read_user_by_id: считывание пользователя по id не выполнено")
            raise HTTPException(status_code = 505, detail = f"ошибка в поиске пользователя {e}")



    async def update_user(
            self,
            session: AsyncSession,
            user_id = int,
            user_data = UserSchema 
            ) -> UserModel:
        try:
            logger.info(f"update_user: обновление пользователя по id {user_id}")

            user = await self.read_user_by_id(session,user_id)

            user.username = user_data.username
            user.email = user_data.email
            user.password = user_data.password
            
            await session.commit()
            await session.refresh(user)
            logger.info(f"Users.read_user_by_id: Пользователь с ID {user_id} обновлен")
            return user
        
        except Exception as e:
            logger.error(f"Пользователь {e} не обновлен")
            raise HTTPException(status_code = 500, detail = f"ошибка в обновлении пользователя {e}")
    
    
    
    async def delete_user(
            self,
            session:AsyncSession,
            user_id: int,
            ) -> dict:
        try:
            logger.info(f"delete_user: Удаление пользователя с ID {user_id}")

            user = await self.read_user_by_id(session, user_id)

            await session.delete(user)
            await session.commit()

            return {
                "status": "success",
                "message": f"Пользователь '{user.username}' успешно удален",
                "deleted_book_id": user_id
            }
        except Exception as e:
            logger.error(f"Пользователь {e} не удален")
            raise HTTPException(status_code = 500, detail = f"Ошибка при удалении пользователя {str(e)}")
    

