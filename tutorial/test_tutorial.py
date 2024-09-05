from fastapi.testclient import TestClient

from tutorial.tutorial import app, Item

client = TestClient(app)

def test_read_item():
    response = client.get("/items/3")
    assert response.status_code == 200
    assert response.json()["item_id"] == 3


my_item = Item(
    name="TV",
    description="A simple TV",
    price=200.00,
    tax=0.1,
)

def test_create_item():
    response = client.post("/items", json=my_item.model_dump())
    assert response.status_code == 201
    ret = response.json()
    assert ret["name"] == my_item.name
    assert ret["description"] == my_item.description
    assert ret["price"] == my_item.price
    assert ret["tax"] == my_item.tax

def test_create_same_item():
    response = client.post("/items", json=my_item.model_dump())
    assert response.status_code == 409
