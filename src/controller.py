"""
Controller implement only the API logic, separating it from the other logic.
"""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src import classes, handler
from src.classes import UserResponse, UserDB, Token
from src.handler import get_current_user #, get_user

##### USER ENDPOINTS #######
"""
User endpoints will be defined here.
Therefore, a separate router is created. It has the prefix "/users"
All endpoints which are wrapped with this router will start with "/users".
"""

user_router = APIRouter(prefix="/users", tags=["Users"])    # tags define metadata for documentation purposes

@user_router.post("/", status_code=201)
async def create_user(user: classes.UserSchema) -> None:
    """
    An endpoint to create a new user.
    """

    return handler.create_user(user)


"""
Multiple "advanced" stuff is happening here.

First of all, the user is automatically retrieved via Depends. Depends is essentially a function, which FastAPI will
automatically execute if the endpoint is accessed. 
If the user has logged in, they will receive a token. This token must be send in the header of the request in the form of:
{"Authorization": f'Bearer {access_token}'}
OpenAPI Docs will do that for you. 
The token contains user information, with witch the user will be retrieved with.
The endpoint is restricted, a "Not Authenticated" exception will be raised if the token is not provided, invalid or expired.

Second, we can see some FastAPI "magic" here:
user is of type UserDB, which is also indicated in the return type. Otherwise we would get a warning and "confuse" the 
IDE, so that it would eventually provide wrong code completion information.
However, UserDB contains the hashed password, which we should not return. Therefore, we defined a separate UserResponse
class. It is indicated as response_model in the endpoint wrapper. With that, FastAPI will automatically cast the user 
from type UserDB to UserResponse, removing the password in the response.

A "classical" approach is commented out below (calls a commented function in handler). 
"""
@user_router.get("/profile", status_code=200, response_model=UserResponse)
async def get_user(user: UserDB = Depends(get_current_user)) -> UserDB:
    """
    Returns the user's profile information. User parameter is automatically resolved. User must be authenticated.
    """

    return user

# Alternative without FastAPI "Magic"
"""@user_router.get("/profile", status_code=200)
async def get_user(user: UserDB = Depends(get_current_user)) -> UserResponse:
    return handler.get_user(user)"""



###### LOGIN ENDPOINT #########
"""
Login endpoints will be defined here.
Therefore, a separate router is created. It has the prefix "/login"
All endpoints which are wrapped with this router will start with "/login".

In bigger applications, you would move each router to a new file.
"""

login_router = APIRouter(prefix="/login", tags=["Login"])

@login_router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> dict[str, str]:
    """
    The endpoint provides a login functionality for users.
    The endpoint expects a form data body (not json) like
    {"username": {user_email}, "password": {password}}

    It returns
    {"access_token": access_token, "token_type": "bearer"}
    """

    return handler.login_for_access_token(form_data)