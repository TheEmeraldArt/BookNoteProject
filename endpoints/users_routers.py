from fastapi import APIRouter, Depends, HTTPException, status

from fastapi.security import OAuth2PasswordRequestForm

from schema.user_schema import UserSchema, UserOut, Token

from session.session_db import SessionDep

from auth.authentication import get_current_user, require_admin

from database.users_db import UserModel

from auth.authorization import authenticate_user, create_access_token

from CRUD.users import UsersCRUD

from loguru import logger


logger.add(
    "app.log",
    rotation="10 MB",
    retention="30 days",
    level="INFO",
    backtrace=True,
    diagnose=True
)


router = APIRouter(prefix="/auth", tags=["РАБОТА С ПОЛЬЗОВАТЕЛЯМИ 👨‍💻"])

user_crud = UsersCRUD()



@router.post("/register", response_model=UserOut, tags =["CRUD"], summary = "регистрация")
async def register(user: UserSchema, session: SessionDep):
    """Регистрация нового пользователя"""
    return await user_crud.create_user(session, user)



@router.delete("/delete_user/{user_id}",tags =["CRUD"],summary="Удалить пользователя")
async def delete_user_by_id(
    user_id: int,
    session: SessionDep,
    current_user: UserModel = Depends(require_admin)
):
    try:
        logger.info(f"delete_user_by_id: запрос на удаление пользователя {user_id}  принят")

        result = await user_crud.delete_user(session,user_id)
        logger.info("delete_user_by_id: пользователь удален")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"delete_user произошла ошибка {e}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")



@router.put("/update_user/{user_id}", tags =["CRUD"], summary = "Обновить пользователя") 
async def update_user_by_id(
    user_id: int,
    session: SessionDep,
    data: UserSchema,
    current_user: UserModel = Depends(require_admin)
):
    try:
        logger.info("update_user_by_id: запрос на обновление пользователя принят")

        updated_user = await user_crud.update_user(session,user_id,data)
        logger.info("update_user_by_id: пользователь успешно обновлен")
        return  {
            "status": 200,
            "message": "Пользователя обновлен обновлена",
            "book": updated_user
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"update_user_by_id произошла ошибка {e}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")



@router.get("/get_user",response_model= UserSchema, tags =["CRUD"], summary = "Получить пользователя по id" )
async def get_user(
    session: SessionDep,
    id: int,
    current_user: UserModel = Depends(require_admin)
):
    try:
        logger.info("get_user: запрос на получение пользователя принят")
        
        user = await user_crud.read_user_by_id(session,id)
        logger.info("get_user: пользователь спешно получен")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_user произошла ошибка {e}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")



@router.get("/get_all_users", tags =["CRUD"], summary = "Получить всех пользователей")
async def get_users(
    session: SessionDep,
    current_user: UserModel = Depends(require_admin)
) -> list[UserSchema]:
    try:
        logger.info("get_users: запрос на получение всех пользователей принят")

        users = await user_crud.read_all_users(session)
        if not users:
            raise HTTPException(status_code=404, detail="Пользователи не найдены")
        logger.info("get_users: запрос на получение пользователей выполнен")
        return  users
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_users произошла ошибка {e}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")



@router.post("/login", response_model=Token,  tags =["AUTH"], summary = "логгирование" )
async def login(
    session: SessionDep,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Вход и получение токена"""
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}



@router.get("/me", response_model=UserOut, tags =["AUTH"], summary = "текущий пользователь")
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    """Получить информацию о текущем пользователе"""
    return current_user




@router.get("/protected", tags =["AUTH"], summary = "знакомство с пользователем")
async def protected_route(current_user: UserModel = Depends(get_current_user)):
    return {
        "message": f"Hello {current_user.username}!",
        "user_id": current_user.id,
        "email": current_user.email
    }


@router.get("/role",  tags =["AUTH"], summary = "текущая роль пользователя")
async def get_role(current_user: UserModel = Depends(get_current_user)):
    return {
        "role": current_user.role
    }