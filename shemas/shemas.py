from pydantic import BaseModel
from datetime import date
from typing import Optional

class InssueUpdateSchema(BaseModel):
    book_name: Optional[str] = None
    reader_name: Optional[str] = None
    drop_date: Optional[date] = None
    plan_get_date: Optional[date] = None
    real_get_date: Optional[date] = None
    book_lost: Optional[bool] = None
    summ: Optional[int] = None
    date_summ: Optional[date] = None

# Схема для ответов (с полем id)
class InssueResponseSchema(BaseModel):
    id: int
    book_name: str
    reader_name: str
    drop_date: date
    plan_get_date: date
    real_get_date: Optional[date] = None
    book_lost: Optional[bool] = False
    summ: Optional[int] = 0
    date_summ: Optional[date] = None

class BookUpdateShema(BaseModel):
    name: str | None = None
    author: str | None = None
    price: int | None = None
    year: int | None = None
    value: int | None = None

class BookAddShema(BaseModel):
    name: str
    author: str
    price: int
    year: int
    value: int
    
class ReaderAddShema(BaseModel):
    name: str
    address: str

class InssueShema(BaseModel):
    id: int
    book: str
    reader: str
    drop_date: date
    plan_get_date: date
    real_get_date: date | None
    book_lost: bool | None = None
    summ: int |  None = None
    date_summ: date | None = None
    
class InssueAddShema(BaseModel):
    book: str
    reader: str 
    drop_date: date
    plan_get_date: date
    real_get_date: date | None = None
    book_lost: bool | None = None
    summ: int | None = None
    date_summ: date | None = None
