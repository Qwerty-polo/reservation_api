from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.functions import current_user

from models import models
from schemas.schemas import TicketResponse, SessionShortResponse
from database.db import SessionDep
from models.models import Ticket, User, Session
from security.security import get_current_user
from datetime import datetime
router = APIRouter(tags=["Tickets"])

@router.get("/{session_id}/my-tickets", response_model=list[TicketResponse])
async def get_my_tickets_for_session(
        session_id: int,
        db: SessionDep,
        current_user: User = Depends(get_current_user)
):
    # 1. Формуємо запит із підвантаженням сесії та фільму (щоб не було 500 помилки)
    query = (
        select(Ticket)
        .options(joinedload(Ticket.session).joinedload(Session.movie))
        .where(
            Ticket.session_id == session_id,  # Фільтр за сеансом з URL
            Ticket.user_id == current_user.id  # Фільтр за поточним юзером
        )
    )

    # 2. Виконуємо запит (тут await потрібен)
    result = await db.execute(query)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")

    # 3. Отримуємо результат (тут await НЕ потрібен)
    my_tickets = result.scalars().all()

    return my_tickets

@router.get("/my_tickets", response_model=list[TicketResponse])
async def get_my_tickets(db:SessionDep,
                         current_user: User = Depends(get_current_user)
                         ):

    result = await db.execute(select(models.Ticket)
                              .options(joinedload(models.Ticket.session).joinedload(models.Session.movie))
                              .where(models.Ticket.user_id == current_user.id))
    tickets = result.scalars().all()
    if not tickets:
        raise HTTPException(status_code=404, detail="You dint have any tickets yet")


    return tickets


@router.post("/{ticket_id}/buy")
async def buy_tickets(ticket_id: int,
                      db: SessionDep,
                      current_user: User = Depends(get_current_user)
                      ):
    query = (
        select(Ticket)
        .options(joinedload(Ticket.session).joinedload(Session.movie))
        .where(Ticket.id == ticket_id)
    )
    result = await db.execute(query)
    ticket = result.scalar_one_or_none()

    # 2. Перевірки
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.user_id is not None:
        raise HTTPException(status_code=403, detail="You cannot buy this ticket, it's already taken")


    if datetime.now() >= ticket.session.start_time:
        HTTPException(status_code=400, detail="You cannot buy this ticket, it's already taken or started")

    # 3. Купуємо!
    ticket.user_id = current_user.id
    await db.commit()
    await db.refresh(ticket)

    # 4. Повертаємо ВЕСЬ об'єкт квитка.
    # Pydantic сам візьме з нього сесію і фільм та зробить красивий JSON!
    return ticket
@router.patch("/{ticket_id}/reserve")
async def patch_tickets(db:SessionDep,
                        ticket_id: int,
                        current_user: User = Depends(get_current_user)
                        ):

    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="You are not allowed to perform this action.")


    query = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    result = query.scalar()
    if not result:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if result.is_reserved:
        raise HTTPException(status_code=400, detail="Ticket is reserved")

    result.is_reserved = True
    result.user_id = current_user.id

    await db.commit()
    await db.refresh(result)
    return result

@router.delete("/{ticket_id}/reserve")
async def delete_tickets(db:SessionDep,
                         ticket_id: int,
                         current_user: User = Depends(get_current_user)):

    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="You are not allowed to perform this action.")


    result = await db.execute(select(models.Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your ticket!")

    ticket.is_reserved = False
    ticket.user_id = None


    await db.commit()
    return {'message': f'Reservation is canceled, the seat is free again. '}

