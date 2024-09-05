from typing import Annotated

from pydantic import BaseModel, EmailStr, Field


# define base user, which other user classes will inherit from
class UserBase(BaseModel):
    email: EmailStr     # validate automatically that string is email-like

# Database User
class UserDB(UserBase):
    password: str   # will be stored as hash
    personal_info: str|None

# User for Input (creating new user)
class UserSchema(UserBase):
    password: Annotated[str, Field(min_length=8)]   # validate automatically, that password has minimum length of 8
    personal_info: str|None

# Will be used in Responses
class UserResponse(UserBase):
    personal_info: str|None


"""
this is the token class. An object is returned if user logs in.
To access restricted endpoints, user must send this token in the header in the form of:
{"Authorization": f'Bearer {access_token}'}
This is done automatically if using OpenAPI Docs.
"""
class Token(BaseModel):
    access_token: str
    token_type: str

