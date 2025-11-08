from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy import Identity

from session.session_db import  Base



class BookModel(Base):
    __tablename__ = "books"
    
    id: Mapped[int] = mapped_column(Identity(start=1, cycle=True),primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    author: Mapped[str] = mapped_column(nullable=False)

