from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from models import models
from models.models import Movie, User
from schemas.schemas import MovieResponse, MovieCreate, MovieUpdate
from database.db import SessionDep
from security.security import get_current_user

router = APIRouter(tags=["Movies"])

@router.post("/movies", response_model=MovieResponse)
async def create_movie(db: SessionDep,
                       movie: MovieCreate,
                       current_user: User = Depends(get_current_user)
                       ):

    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="You are not allowed to perform this action.")

    # ✨ Розпаковуємо всі поля автоматично знизу приклад як воно виглядало раніше:
    movie_dict = movie.model_dump()

    # 2. ОЦЕЙ КРОК КРИТИЧНИЙ: перетворюємо HttpUrl на звичайний str
    # Бо база даних не розуміє тип HttpUrl
    movie_dict["poster_url"] = str(movie_dict["poster_url"])

    # 3. Створюємо модель, розпакувавши словник (**)
    new_movie = models.Movie(**movie_dict)
    # new_movie = models.Movie(
    #     title=movie.title,
    #     description=movie.description,
    #     poster_url=movie.poster_url,
    # )

    db.add(new_movie)
    await db.commit()
    await db.refresh(new_movie)
    return new_movie

@router.get("/movies", response_model=List[MovieResponse])
async def all_movies(db: SessionDep):
    result = await db.execute(select(Movie))
    return result.scalars().all()


@router.delete("/movies/{movie_id}")
async def delete_movie(db: SessionDep,
                       movie_id: int,
                       current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="You are not allowed to perform this action.")

    result = await db.execute(select(Movie).where(Movie.id == movie_id))
    movie = result.scalar_one_or_none()

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    await db.delete(movie)
    await db.commit()
    return {"message": "Movie deleted"}


@router.patch("/{movie_id}", response_model=MovieResponse)
async def update_movie(
        movie_id: int,
        movie_data: MovieUpdate,  # 👈 Використовуємо нову схему з Optional
        db: SessionDep,
        current_user: User = Depends(get_current_user)
):
    # 1. Перевірка на адміна (якщо у тебе є ця логіка - залишаємо)
    if not getattr(current_user, 'is_admin', True):  # Захист, якщо раптом is_admin ще не налаштовано
        raise HTTPException(status_code=403, detail="You are not allowed to perform this action.")

    # 2. Шукаємо фільм у базі
    query = await db.execute(select(Movie).where(Movie.id == movie_id))
    movie = query.scalar_one_or_none()

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    # 3. Магія оновлення: беремо тільки ті дані, які прислали
    update_data = movie_data.model_dump(exclude_unset=True)

    # Перебираємо всі поля і оновлюємо їх в об'єкті бази даних
    for key, value in update_data.items():
        # Оскільки HttpUrl це спеціальний об'єкт Pydantic, перетворюємо його на рядок для бази
        if key == "poster_url" and value is not None:
            setattr(movie, key, str(value))
        else:
            setattr(movie, key, value)

    # 4. Зберігаємо зміни
    await db.commit()
    await db.refresh(movie)

    return movie
