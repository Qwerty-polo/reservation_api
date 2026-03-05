import os
from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from typing import Annotated

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

class Base(DeclarativeBase):
    pass

engine = create_async_engine(DATABASE_URL, echo=True)

Session_local = async_sessionmaker(
    bind= engine,
    class_=AsyncSession, #необовязково якшо вже зверху вказав шо використовуєш async_sessionmaker
    expire_on_commit=False
)

async def get_db():
#беремо сесії з нашої фабрики яку ми прописали вище
    async with Session_local() as session:
        yield session

#AsyncSession — який тип даних я очікую, Depends(get_db) — звідки FastAPI має ці дані взяти
SessionDep = Annotated[AsyncSession, Depends(get_db)]

