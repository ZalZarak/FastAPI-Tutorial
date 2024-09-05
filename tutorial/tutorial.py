import time
from typing import Annotated

from fastapi import FastAPI, Body, HTTPException, BackgroundTasks
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

@app.get("/items2/{item_id}")
async def read_user_item(
    user_name: str, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "customer_name": user_name}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

items = []

@app.post("/items/", status_code=201)
async def create_item(item: Item) -> Item:
    if item.name in map(lambda x: x.name, items):
        raise HTTPException(status_code=409, detail="Item already exists")
    items.append(item)
    return item

@app.post("/singular_value_in_body")
async def singular_value_in_body(x: Annotated[int, Body()]):
    return x

@app.get("/background_task", status_code=200)
async def background_task(msg: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(delayed_print, msg)

def delayed_print(msg: str):
    time.sleep(5)
    print(f"Hello World, just 5 seconds late. {msg}")