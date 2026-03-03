from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models import models
from models.models import Ticket, Session, User
from schemas.schemas import SessionResponse, SessionCreate
from database.db import SessionDep
from security.security import get_current_user

router = APIRouter(tags=["Sessions"])

@router.post("/session", response_model=SessionResponse)
async def create_session(db:SessionDep,
                         session_data: SessionCreate,
                         current_user: User = Depends(get_current_user)
                         ):

    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="You are not allowed to perform this action.")


    session_dict = session_data.model_dump()

    session_dict["start_time"] = session_dict["start_time"].replace(tzinfo=None)

    new_session = models.Session(**session_dict)

    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)

    for seat_number in range(1, 11):
        new_ticket = models.Ticket(
            session_id=new_session.id,
            seat_number=seat_number,
            is_reserved=False
        )
        db.add(new_ticket)
    await db.commit()

    result = await db.execute(
        select(models.Session)
        .where(models.Session.id == new_session.id)  # 👈 ПЕРЕНЕСИ СЮДИ
        .options(
            joinedload(models.Session.movie),
            joinedload(models.Session.tickets)
        )
    )
    full_session = result.unique().scalar_one()  # unique() потрібен при joinedload на список

    await db.commit()

    return full_session


@router.get("/session", response_model=List[SessionResponse])
async def get_session(db: SessionDep):
    result = await db.execute(
        select(models.Session)
        .options(
            joinedload(models.Session.movie),
            joinedload(models.Session.tickets)  # 👈 ДОДАЛИ ЦЕЙ РЯДОК
        )
    )

    # Використовуємо .unique(), бо joinedload на список (квитки)
    # може дублювати рядки сесій у результаті
    return result.scalars().unique().all()