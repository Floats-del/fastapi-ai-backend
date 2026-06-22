import pytest
from pydantic import TypeAdapter
from jose import jwt
from Oauth2 import settings
from utils.schemas import UserResponseSchema, TokenSchema

def test_create_user(client):
    res = client.post(
        "/users/", 
        json={
            "email": "test@gmail.com",
            "password": "testPass123" 
        }
    )
    assert res.status_code == 201
    new_user = UserResponseSchema(**res.json())
    assert new_user.email == "test@gmail.com"


def test_login_user(client, test_user):
    res = client.post(
        "/login", 
        data={
            "username": test_user['email'],
            "password": test_user['password']
        }
    )
    
    assert res.status_code == 200
    login_res = TokenSchema(**res.json())
    
    assert login_res.token_type == "bearer"
    assert len(login_res.access_token) > 0 
    
    payload: dict = jwt.decode(
        login_res.access_token, 
        key=settings.hash_secret_key, 
        algorithms=[settings.algorithm]
    ) 
    
    user_id_from_payload = payload.get("user_id")
    assert user_id_from_payload == test_user["user_id"]


@pytest.mark.parametrize(
    "email,password,status_code,expected_detail",
    [
        ("wrong@email.com", "password123", 404, "User Not Found!"),
        ("test@test.com", "wrong_pass", 403, "Unauthorized"),
        (None, "password123", 422, None),
        ("test@test.com", None, 422, None),
    ]
)
def test_bad_login(client, test_user, email, password, status_code, expected_detail):
    if email == "test@test.com":
        email = test_user["email"]

    res = client.post(
        "/login",
        data={
            "username": email,
            "password": password
        }
    )

    assert res.status_code == status_code

    if status_code == 422:
        assert "detail" in res.json()
    else:
        assert res.json().get("detail") == expected_detail


def test_get_user_by_id_authed(seeded_users, auth_client_factory):
    user1 = seeded_users["user1"]
    auted_user = auth_client_factory(user1)
    
    res = auted_user.get(f"/users/{user1['user_id']}")
    assert res.status_code == 200
    
    server_response = res.json()
    ta = TypeAdapter(UserResponseSchema)
    validated_user = ta.validate_python(server_response)
    
    assert validated_user.user_id == user1["user_id"]
    assert validated_user.email == user1["email"]


def test_get_all_user_authed(seeded_users, auth_client_factory):
    user1 = seeded_users["user1"]
    auted_user = auth_client_factory(user1)
    
    res = auted_user.get("/users/")
    assert res.status_code == 200
    
    server_response: list = res.json()

    try:
        ta = TypeAdapter(list[UserResponseSchema])
        validated_users = ta.validate_python(server_response)
    except Exception as e:
        pytest.fail(f"User registry array failed validation: {e}")
        
    assert len(validated_users) >= 2
    
    emails = [u.email for u in validated_users]
    assert seeded_users["user1"]["email"] in emails
    assert seeded_users["user2"]["email"] in emails


def test_get_all_users_unauth(client):
    res = client.get("/users/")
    assert res.status_code == 401
    assert res.json()["detail"] == "Not authenticated"
    assert res.headers["WWW-Authenticate"] == "Bearer"


def test_get_user_by_id_unauth(client, seeded_users):
    user1 = seeded_users["user1"]

    res = client.get(f"/users/{user1['user_id']}")
    assert res.status_code == 401
    assert res.json()["detail"] == "Not authenticated"
    assert res.headers["WWW-Authenticate"] == "Bearer"