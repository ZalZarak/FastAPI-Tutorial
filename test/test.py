import copy

from starlette.testclient import TestClient

from src.classes import UserSchema, UserDB
from src.main import app

""" 
in an application which uses a persistent database (which is not deleted on restart), you would create a
testing session of your database and reset it at the end, or create a new database, so that your tests don't alter
the existing database
Tutorial: https://fastapi.tiangolo.com/advanced/testing-database/#create-the-new-database-session
here it is not necessary, since our fake database is not persistent
"""
from src.database import fake_user_db

client = TestClient(app)

# create test user
my_user = UserSchema(email='my_user@email.com', password='12345678', personal_info="I am just a user.")

# global variable to store the login header across the different functions
global user_access_header

def test_create_user_password_to_short():
    my_user2 = copy.deepcopy(my_user)
    my_user2.password = '1234567'

    # model_dump() gives you the dictionary of a pydantic object.
    # body are submitted as json
    response = client.post('users/', json=my_user2.model_dump())

    assert response.status_code == 422, ("status code should be 422 - unprocessable entity, if the user tries to create "
                                         "a password which is not long enough")
    assert len(fake_user_db) == 0

    """
    in a bigger project, you should use assert with error messages, so that developers can see directly
    what went wrong. Like:
    
    assert response.status_code == 422, ("status code should be 422 - unprocessable entity, if the user tries to create "
                                         "a password which is not long enough") 
    
    Here I left it out for simplicity.
    """


def test_create_user():
    response = client.post('users/', json=my_user.model_dump())

    assert response.status_code == 201

    db_user: UserDB = fake_user_db[my_user.email]

    assert db_user.email == my_user.email
    assert db_user.personal_info == my_user.personal_info
    assert db_user.password != my_user.password


def test_create_user_again():
    response = client.post('users/', json=my_user.model_dump())

    assert response.status_code == 409
    assert len(fake_user_db) == 1


def test_login_nonexistent_user():
    form_data = {"username": "random@email.com", "password": "12345678"}

    # this endpoint expects form_data, so pass it as data parameter instead
    response = client.post('/login/token', data=form_data)

    assert response.status_code == 401
    assert "access_token" not in response.json()


def test_login_wrong_password():
    form_data = {"username": my_user.email, "password": "123456789"}

    response = client.post('/login/token', data=form_data)

    assert response.status_code == 401
    assert "access_token" not in response.json()


def test_login():
    form_data = {"username": my_user.email, "password": my_user.password}

    response = client.post('/login/token', data=form_data)

    assert response.status_code == 200
    assert "access_token" in response.json()

    global user_access_header   # access this variable from global scope
    # this is just how the header has to look like
    user_access_header = {"Authorization": f'Bearer {response.json()["access_token"]}'}


def test_get_user():
    # header goes in header
    response = client.get('/users/profile', headers=user_access_header)

    assert response.status_code == 200

    ret = response.json()

    assert ret["email"] == my_user.email
    assert ret["personal_info"] == my_user.personal_info
    assert "password" not in ret.keys()


def test_get_user_wrong_token():
    wrong_token = copy.deepcopy(user_access_header)
    wrong_token['Authorization'] = wrong_token['Authorization'] + '1'

    response = client.get('/users/profile', headers=wrong_token)

    assert response.status_code == 401
