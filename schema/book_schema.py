from pydantic import BaseModel



class BookSchema(BaseModel):
    title: str
    author: str


class BooklIdShcema(BookSchema):
    id: int
    title: str
    author: str


class Config:
        from_attributes = True