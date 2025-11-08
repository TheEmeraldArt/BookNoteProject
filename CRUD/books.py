from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

from fastapi import HTTPException

from loguru import logger

from database.books_db import BookModel

from schema.book_schema import BookSchema




class BooksCRUD:
    """CRUD операции для работы с книгами"""

    async def create_book(
        self,
        session: AsyncSession,
        book_data: BookSchema
    ) -> BookModel:
        """Создание новой книги"""
        try:
            logger.info("Books.create_book: Создание новой книги")
            
            new_book = BookModel(
                title=book_data.title,
                author=book_data.author,
            )

            session.add(new_book)
            await session.commit()
            await session.refresh(new_book)

            logger.info(f"Books.create_book: Книга создана с ID {new_book.id}")
            return new_book
        
        except Exception as e:
            await session.rollback()
            logger.error(f"Произошла ошибка при создании книги: {e}")
            raise HTTPException(status_code=500, detail=f"Ошибка при создании книги: {str(e)}")



    async def read_all_books(
        self,
        session: AsyncSession
    ) -> list[BookModel]:
        """Получение всех книг"""
        try:
            logger.info("Books.read_all_books: Получение всех книг")

            query = select(BookModel)
            result = await session.execute(query)
            books = result.scalars().all()

            logger.info(f"Books.read_all_books: Найдено {len(books)} книг")
            return books
           
        except Exception as e:
            logger.error(f"Books.read_all_books: Ошибка при получении книг - {e}")
            raise HTTPException(status_code=500, detail=f"Ошибка при получении книг: {str(e)}")



    async def read_book_by_id(
        self,
        session: AsyncSession,
        book_id: int
    ) -> BookModel:
        """Получение книги по ID"""
        try:
            logger.info(f"Books.read_book_by_id: Поиск книги с ID {book_id}")

            query = select(BookModel).where(BookModel.id == book_id)
            result = await session.execute(query)
            book = result.scalar_one_or_none()

            if not book:
                logger.warning(f"Books.read_book_by_id: Книга с ID {book_id} не найдена")
                raise HTTPException(status_code=404, detail = f"Книга не найдена")
            
            logger.info(f"Books.read_book_by_id: Книга с ID {book_id} найдена")
            
            return book
        
        except Exception as e:
            logger.error(f"Books.read_book_by_id: Ошибка при поиске книги - {e}")
            raise HTTPException(status_code=500, detail=f"Ошибка при поиске книги: {str(e)}")
        


    async def update_book(
            self,
            session: AsyncSession,
            book_id: int,
            update_data: BookSchema
    )-> BookModel: 
        try:
            logger.info(f"Books.update_book: Обновление книги с ID {book_id}")

            book = await self.read_book_by_id(session,book_id)

            book.title = update_data.title
            book.author = update_data.author

            await session.commit()
            await session.refresh(book)


            logger.info(f"Books.update_book: Книга с ID {book_id} обновлена")

            return book
        
        except Exception as e:
            await session.rollback()
            logger.error(f"Books.update_book: Ошибка при обновлении книги - {e}")
            raise HTTPException(status_code=500, detail=f"Ошибка при обновлении книги: {str(e)}")



    async def delete_book(
            self,
            session: AsyncSession,
            book_id: int
    ) -> dict: 
        try:
            logger.info(f"Books.delete_book: Удаление книги с ID {book_id}")

            book = await self.read_book_by_id(session, book_id)

            await session.delete(book)
            await session.commit()

            logger.info(f"Books.delete_book: Книга с ID {book_id} удалена")

            return {
                "status": "success",
                "message": f"Книга '{book.title}' успешно удалена",
                "deleted_book_id": book_id
            }
        
        except Exception as e:
            await session.rollback()
            logger.error(f"Books.delete_book: Ошибка при удалении книги - {e}")
            raise HTTPException(status_code=500, detail=f"Ошибка при удалении книги: {str(e)}")

































































