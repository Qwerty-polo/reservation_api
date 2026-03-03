from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from database.db import SessionDep
from schemas.schemas import UserCreate, Token, UserResponse
from auth.auth import verify_password, get_password_hash, create_access_token
from models.models import User

router = APIRouter(tags=["Auth"])


@router.post('/register', response_model=UserResponse)
async def register_user(user_data: UserCreate,
                        db: SessionDep,
                        ):
    result = await db.execute(select(User).where(User.email == user_data.email))
    user_one = result.scalar_one_or_none()

    if user_one is not None:
        raise HTTPException(status_code=400, detail="Email already registered")

    hash_pass = get_password_hash(user_data.password)

    new_user = User(
        email = user_data.email,
        password = hash_pass
    )


    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post('/login', response_model=Token)
async def login_user(
        db: SessionDep,
        form_data: OAuth2PasswordRequestForm = Depends(),
        ):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user_one = result.scalar_one_or_none()

    if not user_one or not verify_password(form_data.password, user_one.password):
        # Помилка 401 - Неавторизований
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    # створюєм свій час життя в auth.py прописав для чого в коментарях
    my_expire_time = timedelta(minutes=60)

    access_token = create_access_token(
        data={"sub": user_one.email},
        expires_delta=my_expire_time
    )

    return {'access_token': access_token, 'token_type': 'bearer', 'is_admin': user_one.is_admin}
