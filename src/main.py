"""
This is the main class, which bundles the entire rest into one app.
"""

from fastapi import FastAPI

from src.controller import user_router, login_router

app = FastAPI()

# import the defined routers, which themselves root forward to endpoints
app.include_router(user_router)
app.include_router(login_router)
