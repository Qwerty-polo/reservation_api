# dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
import jwt

from jwt.exceptions import PyJWTError  # Це для відлову помилок

from database.db import SessionDep
from models.models import User

# Імпортуємо налаштування, які ми винесли нагору в auth.py
from auth.auth import SECRET_KEY, ALGORITHM




# 1. Ця штука каже FastAPI: "Токени брати з ручки /login"
# Це потрібно, щоб у Swagger з'явилася форма логіну при натисканні на замочок
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def get_current_user(
        db: SessionDep,
        token: str = Depends(oauth2_scheme) # FastAPI сам дістане токен і покладе сюди
        ):
    # Заготовка помилки (401), яку ми будемо кидати, якщо щось не так
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 3. РОЗШИФРОВКА: Пробуємо прочитати токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 4. ДІСТАЄМО ДАНІ: Шукаємо там поле 'sub' (де ми сховали імейл)
        email: str = payload.get("sub")

        if email is None:
            raise credentials_exception

    except PyJWTError:  # Якщо токен невалідний
        raise credentials_exception

        # 5. ПОШУК В БАЗІ: Чи є такий юзер насправді?
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    # 6. УСПІХ: Повертаємо живого юзера
    return user
