"""
The handler implements "higher-level" logic which is not connected to API.
"""

from datetime import timedelta, datetime

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from src import service
from src.classes import UserSchema, UserDB, UserResponse
from src.service import add_user_to_db, get_user_from_db, verify_password

from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError


####### USER HANDLER #########
"""
The functions, which the User Controller calls are defined here.
"""


def create_user(user: UserSchema) -> None:
    """
    Create a user, raise HTTPException if exists.
    """

    user = UserDB(**user.model_dump())  # cast user from UserSchema to UserDB

    user.email = user.email.lower()     # make email lower case
    user.password = service.encode_password(user.password)  # hash password

    try:
        add_user_to_db(user)
    except KeyError:
        raise HTTPException(409, "User already exists")


# for an alternative without FastAPI "Magic"
"""def get_user(user: UserDB) -> UserResponse:
    response_user = UserResponse(**user.model_dump(exclude={"password"}))
    return response_user"""


####### LOGIN HANDLER #########
"""
The functions, which the Login Controller and restricted endpoints call (as Depends()), are defined here.

In bigger applications, you would move this handler to a new file.
"""

# some security definitions

# the access token is encrypted with this key
# DON'T do it like that, create random JWT_KEY and read it from a file.
JWT_KEY = "4976bc345151db1c35c2923a2463f0bf870b083a41afdf2b8e3f5057e61589ea"

# encryption algorithm for token
ALGORITHM = "HS256"

# Defines the scheme, which clients have to follow if the want to access restricted endpoints.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/token")

# Defines expiration time for token
ACCESS_TOKEN_EXPIRE_MINUTES = 30

"""
This function creates an encoded token. It takes the provided data, calculates the expiration time and
encodes that using the defined algorithm and jwt_key.
"""
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_KEY, algorithm=ALGORITHM)
    return encoded_jwt

"""
This function is called if a user tries to login in.
form_data is of type OAuth2PasswordRequestForm, which has the parameters username and password.
In security, it is advisable to use industry standards like OAuth2, instead of creating your own solution, especially
if you are not exactly sure what you are doing.
"""
def login_for_access_token(form_data: OAuth2PasswordRequestForm) -> dict[str, str]:
    try:
        user = get_user_from_db(form_data.username)
    except KeyError:
        raise HTTPException(401, "User not found")

    verified = verify_password(form_data.password, user.password)

    if not verified:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        {"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {"access_token": access_token, "token_type": "bearer"}   # This is just how you do it


"""
This is the function Depends calls.
token is defined as another Depends of the above oath2_scheme. Here, FastApi will automatically resolve it, so that
it reads the token from the provided header.
"""
def get_current_user(token: str = Depends(oauth2_scheme)) -> UserDB:
    try:
        payload = jwt.decode(token, JWT_KEY, algorithms=[ALGORITHM])    # decode the token with the key.
        email: str = payload.get("sub")     # read the email from it, which we put there when user logged in.
        if email is None or email == "":
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )

    return get_user_from_db(email)  # return the user associated with this mail

