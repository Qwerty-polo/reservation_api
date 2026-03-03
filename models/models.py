from datetime import datetime

from pydantic import EmailStr
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, Boolean, ForeignKey, DateTime
from database.db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    password: Mapped[str]
    is_admin: Mapped[bool] = mapped_column(default=False)

    tickets: Mapped[list["Ticket"]] = relationship(back_populates="user")

class Movie(Base):
    __tablename__ = "movies"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    poster_url: Mapped[str]

    sessions: Mapped[list["Session"]] = relationship(back_populates="movie")

class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(primary_key=True)

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"))
    start_time: Mapped[datetime]

    movie: Mapped["Movie"] = relationship(back_populates="sessions")
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="session")

class Ticket(Base):
    __tablename__ = "tickets"
    id: Mapped[int] = mapped_column(primary_key=True)
    seat_number: Mapped[int]
    is_reserved: Mapped[bool]


    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"))

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    session: Mapped["Session"] = relationship(back_populates="tickets")
    user: Mapped["User | None"] = relationship(back_populates="tickets")