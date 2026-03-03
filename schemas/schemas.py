from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, ConfigDict, Field, EmailStr

# 1. СПОЧАТКУ МОДЕЛІ ФІЛЬМІВ
class MovieCreate(BaseModel):
    title: str
    description: str = Field(max_length=400)
    poster_url: HttpUrl

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = Field(None, max_length=400)
    poster_url: Optional[HttpUrl] = None

class MovieResponse(BaseModel):
    id: int
    title: str
    description: str
    poster_url: HttpUrl
    model_config = ConfigDict(from_attributes=True)


class TicketInSession(BaseModel):
    id: int
    seat_number: int
    user_id: Optional[int] = None  # Бачимо, чи зайняте місце
    model_config = ConfigDict(from_attributes=True)

class SessionCreate(BaseModel):
    movie_id: int
    start_time: datetime = Field(
        description="Data and time in format: YYYY-MM-DD HH:MM",
        examples=["2026-02-25 19:00"]
    )

class SessionResponse(BaseModel):
    id: int
    movie: MovieResponse
    start_time: datetime
    tickets: List[TicketInSession] = [] # 👈 Використовуємо легку схему
    model_config = ConfigDict(from_attributes=True)

class SessionShortResponse(BaseModel):
    id: int
    movie: MovieResponse
    start_time: datetime

    model_config = ConfigDict(from_attributes=True)

class TicketResponse(BaseModel):
    id: int
    session_id: int
    seat_number: int
    user_id: Optional[int] = None
    session: SessionShortResponse # Тут буде вся інфа про фільм і час
    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    is_admin: bool