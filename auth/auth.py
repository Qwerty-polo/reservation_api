import os

from dotenv import load_dotenv
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#deprecated auto - якшо хтось зайде з старим типом хешу він переробиця автоматично на найновіший
#schema це алгоритм за яким ми шифруємо може бути sha256, або md5 (це старіші)
pwd_context = CryptContext(schemes=['pbkdf2_sha256'], deprecated='auto')



def create_access_token(data: dict, expires_delta: timedelta):
    # 1. Робимо копію даних, щоб не зіпсувати оригінал
    to_encode = data.copy()

    #завдяки цьому ми можемо самі виставляти час для джвт токенна
    #і потім можна буде зробити кнопку запамятати мене на фронті
    #і ти будеш залогінений 7 днів або скільки напишеш
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # 3. Додаємо цей час у дані
    to_encode.update({"exp": expire})
    # 4. Шифруємо все це у рядок
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(user_unhashed_password: str, password: str):
    return pwd_context.verify(user_unhashed_password, password)


