import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Oauth2 import create_access_token
from code1 import app 
from db import Base, get_db
from routers import users
from utils.config import settings
from db_tables.tables import PostTable

DATABASE_URL = (
    f"postgresql://{settings.database_username}:{settings.database_password}"
    f"@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"
) 

engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=10)
Testing_SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine) 

app.include_router(router=users.router)


@pytest.fixture(name="session")
def session_fixture():
    Base.metadata.create_all(bind=engine) 
    db = Testing_SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine) 


@pytest.fixture(name="client")
def client_fixture(session):
    def override_get_db():
        try:
            yield session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture 
def test_user(client):
    user_data = {
        "email": "123@email.com",
        "password": "123passeh"
    }
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture
def test_users(client):
    def create_user(email, password):
        user_data = {
            "email": email,
            "password": password
        }
        res = client.post("/users/", json=user_data)
        assert res.status_code == 201

        user: dict = res.json()
        user["password"] = password
        return user
    return create_user


@pytest.fixture
def seeded_users(test_users):
    return {
        "user1": test_users("123@gmail.com", "123pass"),
        "user2": test_users("456@gmail.com", "456pass")
    }


@pytest.fixture
def test_posts(seeded_users, session):
    user1 = seeded_users["user1"]
    user2 = seeded_users["user2"]

    posts = [
        PostTable(title="p1", content="c1", user_id=user1["user_id"]),
        PostTable(title="p2", content="c2", user_id=user1["user_id"]),
        PostTable(title="p3", content="c3", user_id=user2["user_id"]),
    ]

    session.add_all(posts)
    session.commit()

    for p in posts:
        session.refresh(p)

    return posts


@pytest.fixture
def token_factory():
    def create_token(user_id: int):
        return create_access_token({"user_id": user_id})
    return create_token


@pytest.fixture
def auth_client_factory(client, token_factory):
    def create_auth_client(user):
        token = token_factory(user["user_id"])
        return TestClient(
            client.app,
            headers={"Authorization": f"Bearer {token}"}
        )
    return create_auth_client