import time
import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


def create_test_user(client, username=None, password="1234"):
    """
    Helper function to create a user ONLY when needed.
    """
    if username is None:
        username = f"user_{time.time()}"

    response = client.post("/api/accountCreate", json={
        "username": username,
        "password": password,
        "websites": []
    })

    assert response.status_code in [200, 201]

    return username


# =========================
# CLEANUP (runs after each test)
# =========================
@pytest.fixture(autouse=True)
def cleanup():
    yield
    try:
        from api import collection  # Mongo collection
        collection.delete_many({})
    except Exception as e:
        print("Cleanup failed:", e)


# =========================
# 1. HEALTH CHECK
# =========================
def test_health():
    res = client.get("/health")

    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


# =========================
# 2. ACCOUNT CREATE
# =========================
def test_account_create():
    #no need to use helper function, as we need a unique username here
    username = f"user_{time.time()}"

    res = client.post("/api/accountCreate", json={
        "username": username,
        "password": "1234",
        "websites": []   # for pydantic model of User
    })

    print(res.status_code, res.text)

    assert res.status_code in [200, 201]


# =========================
# 3. LOGIN TEST
# =========================
def test_login():
    username = create_test_user(client)

    # create account first
    client.post("/api/accountCreate", json={
        "username": username,
        "password": "1234",
        "websites": []
    })

    # login
    res = client.post("/api/login", json={
        "username": username,
        "password": "1234"
    })

    print(res.status_code, res.text)

    assert res.status_code == 200


# =========================
# 4. ADD SITE TEST
# =========================
def test_add_site():
    username = create_test_user(client)

    res = client.post("/api/addSite", json={
        "username": username,
        "password": "1234",
        "websites": [
            {
                "site_name": "google",
                "site_username": "user1",
                "site_password": "pass1"
            }
        ]
    })

    print(res.status_code, res.text)

    assert res.status_code in [200, 201]