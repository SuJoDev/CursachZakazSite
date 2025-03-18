from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase, selectinload
from sqlalchemy import select, ForeignKey

from datetime import date

class Base(DeclarativeBase):
    pass

class StuffModel(Base):
    __tablename__ = "Stuffs"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement= True)
    role_id: Mapped[str] = mapped_column()
    login: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()

class BookModel(Base):
    __tablename__ = "Books"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement= True)
    name: Mapped[str] = mapped_column()
    author: Mapped[str] = mapped_column()
    year: Mapped[int] = mapped_column()
    price: Mapped[int] = mapped_column()
    value:Mapped[int] = mapped_column()
    
    inssue: Mapped[list["InssueModel"]] = relationship("InssueModel", back_populates="book")  
    
class ReaderModel(Base):
    __tablename__ = "Readers"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement= True)
    name: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column()
    
    inssue: Mapped[list["InssueModel"]] = relationship("InssueModel", back_populates="reader")   
     
class InssueModel(Base):
    __tablename__ = "Inssues"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement= True)
    book_id: Mapped[int] = mapped_column(ForeignKey("Books.id"))
    reader_id: Mapped[int] = mapped_column(ForeignKey("Readers.id"))
    drop_date: Mapped[date] = mapped_column()
    plan_get_date: Mapped[date] = mapped_column()
    real_get_date: Mapped[date] = mapped_column()
    book_lost: Mapped[bool] = mapped_column()
    summ: Mapped[int] = mapped_column()
    date_summ: Mapped[date] = mapped_column()
    
    book:Mapped["BookModel"] = relationship("BookModel", back_populates="inssue")
    reader: Mapped["ReaderModel"] = relationship("ReaderModel", back_populates="inssue")