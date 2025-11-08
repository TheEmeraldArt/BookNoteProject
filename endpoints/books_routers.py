from fastapi import FastAPI, HTTPException, APIRouter, Depends

from schema.book_schema import BookSchema, BooklIdShcema 

from session.session_db import SessionDep

from auth.authentication import get_current_user

from database.users_db import UserModel

from loguru import logger

from CRUD.books import BooksCRUD




logger.add(
    "app.log",
    rotation="10 MB",
    retention="30 days",
    level="INFO",
    backtrace=True,
    diagnose=True
)



router = APIRouter(prefix="/books", tags=["РАБОТА С КНИГАМИ 📚"])

book_crud = BooksCRUD()


@router.post("/add_book", summary= "Добавить книгу")
async def add_book(
        data: BookSchema,
        session: SessionDep,
        current_user: UserModel = Depends(get_current_user)
    ):
    """Добавить книги"""
    try:
        logger.info("add_book:Данные пришли из API, принято")
        new_book = await book_crud.create_book(session,data)
        logger.info("add_book:Данные добавлены")
        return {"status": 200, "books":  new_book}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"add_book произошла ошибка {e}")



@router.get("/get_books", summary= "Получить все книги")
async def get_books(
        session: SessionDep,
        current_user: UserModel = Depends(get_current_user)
    ) -> list[BooklIdShcema]:
    try:
        logger.info("get_books: запрос получение всех книг принят")
        books = await book_crud.read_all_books(session)
        
        if not books:
            raise HTTPException(status_code=404, detail="Книги не найдены")
        logger.info("get_books: запрос на все книги выполнен")
        return books
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_books произошла ошибка {e}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")
    
        

@router.get("/get_book",response_model= BookSchema, summary= "Получить книгу по id")
async def get_book(
        session: SessionDep,
        id: int,
        current_user: UserModel = Depends(get_current_user)
    ):
    try:
        logger.info("get_book: запрос на получение книги по id принят")
        book = await book_crud.read_book_by_id(session, id)
        logger.info("get_book: запрос на получение книги по id выполнен")
        return book
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_book произошла ошибка {e}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")
    


@router.put("/update_book/{book_id}", summary="Обновить книгу")
async def update_book(
    book_id: int,
    data: BookSchema,
    session: SessionDep,
    current_user: UserModel = Depends(get_current_user)
):
    """Обновить книгу"""
    try:
        logger.info("update_book: заспрос на обновление книги принят")
        updated_book = await book_crud.update_book(session, book_id, data)
        logger.info("update_book: заспрос на обновление книги выполнен")
        return {"status": 200, "message": "Книга обновлена", "book": updated_book}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"update_book произошла ошибка {e}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")



@router.delete("/delete_book/{book_id}", summary="Удалить книгу")
async def delete_book(
    book_id: int,
    session: SessionDep,
    current_user: UserModel = Depends(get_current_user)
):
    """Удалить книгу"""
    try:
        logger.info("delete_book: заспрос на удаление книги принят")
        result = await book_crud.delete_book(session, book_id)
        logger.info("delete_book: заспрос на удаление книги выполнен")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"delete_book произошла ошибка {e}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")