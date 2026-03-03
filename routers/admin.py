from fastapi import APIRouter, Depends, HTTPException

from database.db import SessionDep
from models.models import User, Ticket, Movie
from security.security import get_current_user
from sqlalchemy import select, func


router = APIRouter(prefix="/admin" ,tags=["admin"])

@router.get("/dashboard")
async def dashboard(db: SessionDep,
                    current_user: User = Depends(get_current_user),
                    ):
    if not current_user.is_admin:
        raise HTTPException(status_code=403)

    user_query = await db.execute(select(func.count(User.id)))
    total_users = user_query.scalar()

    movie_query = await db.execute(select(func.count(Movie.id)))
    total_movies = movie_query.scalar()

    tickets_query = await db.execute(select(func.count(Ticket.id)))
    total_tickets = tickets_query.scalar()


    return {"message": f"Hello, {current_user.email}!",
            "stats": {
                "total_users": total_users,
                "total_movies": total_movies,
                "total_tickets": total_tickets
            }}