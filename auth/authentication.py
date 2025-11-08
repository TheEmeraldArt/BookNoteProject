from fastapi import Depends, HTTPException, status

from fastapi.security import OAuth2PasswordBearer

from database.users_db import UserModel

from session.session_db import SessionDep

from auth.authorization import get_current_user_from_token




#Аутетификация - то есть проверка прав доступа 

oauth2_scheme = OAuth2PasswordBearer (tokenUrl="auth/login")


# Текущий пользователь
async def get_current_user(
    session: SessionDep,                   
    token: str = Depends(oauth2_scheme)  
)-> UserModel:
    """Зависимость для получения текущего пользователя"""
    return await get_current_user_from_token(token,session)



# Админ роль
def require_admin(user: UserModel = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return user
