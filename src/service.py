"""
Service implements low-level logic, like (fake)-database transaction/calls
"""

from passlib.context import CryptContext

from src.classes import UserDB
from src.database import fake_user_db

# essentially the algorithm to hash the password
# again, don't create your own solutions, use existing ones - if you are not exactly sure what you are doing.
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def encode_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def add_user_to_db(user: UserDB) -> None:
    # raise error if user exists
    if user.email in fake_user_db.keys():
        raise KeyError("User already registered")

    # save user with key email
    fake_user_db[user.email] = user

def get_user_from_db(email: str) -> UserDB:
    return fake_user_db[email]