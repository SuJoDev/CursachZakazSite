from fastapi import FastAPI, Depends, HTTPException

from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from models.models import *
from shemas.shemas import *


app = FastAPI()

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/BooksShop"

engine = create_async_engine(DATABASE_URL)
new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

@app.post("/api/v1/SignIn")
async def auth_reader(session: SessionDep, login: str, password: str):
    query = select(StuffModel).where(StuffModel.login == login)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    
    if password != user.password:
        raise HTTPException(status_code=400
        )
        
    return user.role_id

@app.post("/api/reader/SignIn")
async def auth(session: SessionDep, name: str, password: str):
    query = select(ReaderModel).where(ReaderModel.name == name)
    result = await session.execute(query)
    
    user = result.scalar_one_or_none()
    
    if "123" != password:
        raise HTTPException(status_code=400
        )

    return user.name

@app.get("/filler")
async def filler(session: SessionDep, book: str):
    query = select(BookModel.price).where(BookModel.name == book)
    result = await session.execute(query)
    return result.scalars().all()

@app.get("/books")
async def get_books(session: SessionDep):
    result = await session.execute(select(BookModel))
    return result.scalars().all()

@app.get("/books/prive")
async def get_price(sesssion: SessionDep, name: str):
    result = await sesssion.execute(select(BookModel).where(BookModel.name == name))
    return result.scalars().all()

@app.get("/reader")
async def get_reader(session: SessionDep):
    result = await session.execute(select(ReaderModel))
    return result.scalars().all()

@app.get("/inssue")
async def get_insue(session: SessionDep):
    qeury = select(InssueModel).options(
        selectinload(InssueModel.book),
        selectinload(InssueModel.reader)
    ).order_by(InssueModel.reader_id)
    
    result = await session.execute(qeury)
    insue = result.scalars().all()
    
    return [
        InssueShema(
        id = i.id,
        drop_date=i.drop_date,
        plan_get_date=i.plan_get_date,
        real_get_date=i.real_get_date,
        book_lost=i.book_lost,
        summ=i.summ,
        date_summ=i.date_summ,
        book = i.book.name if i.book else None,
        reader = i.reader.name if i.reader else None,
        )
        for i in insue
    ]
    
@app.get("/inssue/id")
async def get_users_inssue(session: SessionDep, id: int):
    qeury = select(InssueModel).where(InssueModel.reader_id == id).options(
        selectinload(InssueModel.book),
        selectinload(InssueModel.reader)
    ).order_by(InssueModel.reader_id)
    
    result = await session.execute(qeury)
    insue = result.scalars().all()
    
    return [
        InssueShema(
        id = i.id,
        drop_date=i.drop_date,
        plan_get_date=i.plan_get_date,
        real_get_date=i.real_get_date,
        book_lost=i.book_lost,
        summ=i.summ,
        date_summ=i.date_summ,
        book = i.book.name if i.book else None,
        reader = i.reader.name if i.reader else None,
        )
        for i in insue
    ]
    
@app.get("/inssue/user")
async def get_insue(session: SessionDep, id: int):
    qeury = select(InssueModel).where(InssueModel.id == id).options(
        selectinload(InssueModel.book),
        selectinload(InssueModel.reader)
    ).order_by(InssueModel.reader_id)
    
    result = await session.execute(qeury)
    insue = result.scalars().all()
    
    return [
        InssueShema(
        id = i.id,
        drop_date=i.drop_date,
        plan_get_date=i.plan_get_date,
        real_get_date=i.real_get_date,
        book_lost=i.book_lost,
        summ=i.summ,
        date_summ=i.date_summ,
        book = i.book.name if i.book else None,
        reader = i.reader.name if i.reader else None,
        )
        for i in insue
    ]

@app.post("/book")
async def add_book(
    book: BookAddShema,
    session: SessionDep
):
    
    try:
            db_book = BookModel(
                name=book.name,
                author=book.author,
                price=book.price,
                year=book.year,
                value=book.value
            )
            session.add(db_book)
            await session.commit()
            await session.refresh(db_book)
            return db_book
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await session.close()
        
@app.put("/inssue/{inssue_id}", response_model=InssueResponseSchema)
async def update_inssue(
    inssue_id: int,
    inssue_data: InssueUpdateSchema,
    session: SessionDep
):
    try:
        # Находим запись в таблице Inssue по её ID
        result = await session.execute(
            select(InssueModel).where(InssueModel.id == inssue_id)
        )
        db_inssue = result.scalars().first()
        if not db_inssue:
            raise HTTPException(status_code=404, detail=f"Запись с ID {inssue_id} не найдена.")

        # Обновляем поля записи на основе данных из схемы
        if inssue_data.book_name is not None:
            # Находим ID книги по её названию
            result = await session.execute(
                select(BookModel.id).where(BookModel.name == inssue_data.book_name)
            )
            book_id = result.scalars().first()
            if not book_id:
                raise HTTPException(status_code=404, detail=f"Книга с названием '{inssue_data.book_name}' не найдена.")
            db_inssue.book_id = book_id

        if inssue_data.reader_name is not None:
            # Находим ID читателя по его имени
            result = await session.execute(
                select(ReaderModel.id).where(ReaderModel.name == inssue_data.reader_name)
            )
            reader_id = result.scalars().first()
            if not reader_id:
                raise HTTPException(status_code=404, detail=f"Читатель с именем '{inssue_data.reader_name}' не найден.")
            db_inssue.reader_id = reader_id

        # Обновляем остальные поля
        if inssue_data.drop_date is not None:
            db_inssue.drop_date = inssue_data.drop_date
        if inssue_data.plan_get_date is not None:
            db_inssue.plan_get_date = inssue_data.plan_get_date
        if inssue_data.real_get_date is not None:
            db_inssue.real_get_date = inssue_data.real_get_date
        if inssue_data.book_lost is not None:
            db_inssue.book_lost = inssue_data.book_lost
        if inssue_data.summ is not None:
            db_inssue.summ = inssue_data.summ
        if inssue_data.date_summ is not None:
            db_inssue.date_summ = inssue_data.date_summ

        # Сохраняем изменения в базе данных
        await session.commit()
        await session.refresh(db_inssue)

        # Извлекаем book_name и reader_name из связанных таблиц
        result = await session.execute(
            select(BookModel.name).where(BookModel.id == db_inssue.book_id)
        )
        book_name = result.scalars().first()

        result = await session.execute(
            select(ReaderModel.name).where(ReaderModel.id == db_inssue.reader_id)
        )
        reader_name = result.scalars().first()

        # Формируем ответ
        response_data = {
            "id": db_inssue.id,
            "book_name": book_name,
            "reader_name": reader_name,
            "drop_date": db_inssue.drop_date,
            "plan_get_date": db_inssue.plan_get_date,
            "real_get_date": db_inssue.real_get_date,
            "book_lost": db_inssue.book_lost,
            "summ": db_inssue.summ,
            "date_summ": db_inssue.date_summ
        }

        return response_data
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
        
@app.put("/book")
async def update_book(
    id: int,
    book: BookUpdateShema,
    session: SessionDep
):
    try:
        result = await session.execute(
            select(BookModel).where(BookModel.id == id)
        )
        db_book = result.scalars().first()
        if not db_book:
            raise HTTPException(status_code=404, detail="Книга не найдена")

        if book.name is not None:
            db_book.name = book.name
        if book.author is not None:
            db_book.author = book.author
        if book.price is not None:
            db_book.price = book.price
        if book.year is not None:
            db_book.year = book.year
        if book.value is not None:
            db_book.value = book.value

        await session.commit()
        await session.refresh(db_book)
        return db_book
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reader")
async def add_reader(session:SessionDep, reader: ReaderAddShema):
    try:
            db_reader = ReaderModel(
                name=reader.name,
                address=reader.address
            )
            session.add(db_reader)
            await session.commit()
            await session.refresh(db_reader)
            return db_reader
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await session.close()

@app.put("/reader")
async def update_book(
    id: int,
    reader: ReaderAddShema,
    session: SessionDep
):
    try:
        result = await session.execute(
            select(ReaderModel).where(ReaderModel.id == id)
        )
        db_reader = result.scalars().first()

        if not db_reader:
            raise HTTPException(status_code=404, detail="Читатель не найден")

        if reader.name is not None:
            db_reader.name = reader.name
        if reader.address is not None:
            db_reader.address = reader.address

        await session.commit()
        await session.refresh(db_reader)
        return db_reader
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import HTTPException

@app.post("/inssue")
async def create_inssue(
    inssue_data: InssueAddShema,
    session: SessionDep
):
    try:
        # Поиск книги
        book = await session.execute(select(BookModel).where(BookModel.name == inssue_data.book))
        book = book.scalar()
        if not book:
            raise HTTPException(status_code=404, detail="Книга не найдена")

        # Поиск читателя
        reader = await session.execute(select(ReaderModel).where(ReaderModel.name == inssue_data.reader))
        reader = reader.scalar()
        if not reader:
            raise HTTPException(status_code=404, detail="Читатель не найден")

        # Создание новой записи
        new_inssue = InssueModel(
            book_id=book.id, 
            reader_id=reader.id,
            drop_date=inssue_data.drop_date,
            plan_get_date=inssue_data.plan_get_date,
            real_get_date=inssue_data.real_get_date,
            book_lost=inssue_data.book_lost,
            summ=inssue_data.summ,
            date_summ=inssue_data.date_summ,
        )

        # Добавление записи в сессию
        session.add(new_inssue)
        await session.commit()
        await session.refresh(new_inssue)

        # Проверка на успешность добавления
        if new_inssue.id:
            return {
                "message": "Запись успешно добавлена",
                "id": new_inssue.id,
                "details": {
                    "book_id": new_inssue.book_id,
                    "reader_id": new_inssue.reader_id,
                    "drop_date": new_inssue.drop_date,
                    "plan_get_date": new_inssue.plan_get_date,
                    "real_get_date": new_inssue.real_get_date,
                    "book_lost": new_inssue.book_lost,
                    "summ": new_inssue.summ,
                    "date_summ": new_inssue.date_summ,
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Ошибка при добавлении записи")

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@app.put("/inssue/{inssue_id}")
async def update_inssue(
    inssue_id: int,
    inssue_data: InssueShema,
    session: SessionDep
):
    inssue = await session.execute(select(InssueModel).where(InssueModel.id == inssue_id))
    inssue = inssue.scalar()
    if not inssue:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    book = await session.execute(select(BookModel).where(BookModel.id == inssue_data.book_id))
    if not book.scalar():
        raise HTTPException(status_code=404, detail="Книга не найдена")

    reader = await session.execute(select(ReaderModel).where(ReaderModel.id == inssue_data.reader_id))
    if not reader.scalar():
        raise HTTPException(status_code=404, detail="Читатель не найден")

    inssue.book_id = inssue_data.book_id
    inssue.reader_id = inssue_data.reader_id
    inssue.drop_date = inssue_data.drop_date
    inssue.plan_get_date = inssue_data.plan_get_date
    inssue.real_get_date = inssue_data.real_get_date
    inssue.book_lost = inssue_data.book_lost
    inssue.summ = inssue_data.summ
    inssue.date_summ = inssue_data.date_summ

    await session.commit()
    await session.refresh(inssue)

    return {"message": "Запись успешно обновлена", "id": inssue.id}
