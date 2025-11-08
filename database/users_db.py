from sqlalchemy.orm import  Mapped, mapped_column
from sqlalchemy import Identity, Enum as SQLEnum
from session.session_db import Base

class UserModel(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Identity(start=1, cycle=True),primary_key=True)
    email: Mapped[str] = mapped_column(nullable=False,unique=True)
    username: Mapped[str] = mapped_column(nullable=False,unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(default='user', nullable=False)




