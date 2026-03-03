from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import select

from auth.auth import get_password_hash
from database.db import engine, Base
from models import models
from models.models import User
from database.db import Session_local

from routers.movies import router as movies_router
from routers.sessions import router as sessions_router
from routers.tickets import router as tickets_router
from routers.users import router as users_router
from routers.admin import router as admin_router
from fastapi.middleware.cors import CORSMiddleware

# --- ФУНКЦІЯ ПЕРЕВІРКИ ТА СТВОРЕННЯ АДМІНА ---
async def create_first_admin():
    # Список імейлів, які мають бути адмінами
    ADMINS_TO_CREATE = [
        {"email": "admin@example.com", "pass": "12345"},
    ]
    # Відкриваємо асинхронну сесію вручну
    async with Session_local() as db:
        for admin_data in ADMINS_TO_CREATE:
            result = await db.execute(select(User).where(User.email == admin_data["email"]))
            if not result.scalar_one_or_none():
                new_admin = User(
                    email=admin_data["email"],
                    password=get_password_hash(admin_data["pass"]),
                    is_admin=True
                )
                db.add(new_admin)
        await db.commit()

# --- ФУНКЦІЯ СТВОРЕННЯ ТАБЛИЦЬ ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Цей код виконується при запуску сервера
    async with engine.begin() as conn:
        # Створюємо всі таблиці, які описані в models.py
        await conn.run_sync(Base.metadata.create_all)
    print("check if admin is exist")
    await create_first_admin()
    yield
app = FastAPI(lifespan=lifespan, title = "Reservation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(movies_router)
app.include_router(sessions_router)
app.include_router(tickets_router)
app.include_router(users_router)
app.include_router(admin_router)
