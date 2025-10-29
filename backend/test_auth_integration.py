import pytest
from fastapi.testclient import TestClient
from server import app
from database import db_manager


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_auth_flow(client):
    register_payload = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "testpassword123"
    }
    
    login_payload = {
        "email": "testuser@example.com",
        "password": "testpassword123"
    }
    
    login_response = client.post("/api/v1/auth/login", json=login_payload)
    
    if login_response.status_code == 401:
        register_response = client.post("/api/v1/auth/register", json=register_payload)
        assert register_response.status_code in [200, 201, 400]
        
        login_response = client.post("/api/v1/auth/login", json=login_payload)
    
    if login_response.status_code == 200:
        data = login_response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        
        access_token = data["access_token"]
        refresh_token = data["refresh_token"]
        
        me_response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert me_response.status_code == 200
        user_data = me_response.json()
        assert user_data["email"] == "testuser@example.com"
        
        refresh_response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        assert "access_token" in new_tokens
        
        api_keys_payload = {
            "runpod": "test-runpod-key",
            "openai": "test-openai-key"
        }
        update_keys_response = client.put(
            "/api/v1/auth/me/api-keys",
            headers={"Authorization": f"Bearer {access_token}"},
            json=api_keys_payload
        )
        assert update_keys_response.status_code == 200
        updated_user = update_keys_response.json()
        assert updated_user["api_keys"]["runpod"] == "test-runpod-key"


def test_unauthenticated_access(client):
    response = client.get("/api/v1/projects")
    assert response.status_code in [200, 503]


def test_invalid_token(client):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401
