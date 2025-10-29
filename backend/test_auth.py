import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from services.auth_service import AuthService
from repositories.user_repository import UserRepository


@pytest.fixture
def mock_user_repo():
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def auth_service(mock_user_repo):
    return AuthService(mock_user_repo)


@pytest.mark.asyncio
async def test_register_user_success(auth_service, mock_user_repo):
    mock_user_repo.find_by_email.return_value = None
    mock_user_repo.find_by_username.return_value = None
    mock_user_repo.create.return_value = None
    
    user = await auth_service.register_user("test@example.com", "testuser", "password123")
    
    assert user["email"] == "test@example.com"
    assert user["username"] == "testuser"
    assert "hashed_password" not in user
    assert user["api_keys"] == {"runpod": None, "openai": None, "civitai": None}
    mock_user_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_register_user_duplicate_email(auth_service, mock_user_repo):
    mock_user_repo.find_by_email.return_value = {"id": "existing"}
    
    with pytest.raises(ValueError, match="Email already registered"):
        await auth_service.register_user("test@example.com", "testuser", "password123")


@pytest.mark.asyncio
async def test_authenticate_user_success(auth_service, mock_user_repo):
    hashed_password = AuthService.hash_password("password123")
    mock_user_repo.find_by_email.return_value = {
        "id": "user123",
        "email": "test@example.com",
        "username": "testuser",
        "hashed_password": hashed_password,
        "is_active": True
    }
    
    user = await auth_service.authenticate_user("test@example.com", "password123")
    
    assert user is not None
    assert user["id"] == "user123"
    assert "hashed_password" not in user


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(auth_service, mock_user_repo):
    hashed_password = AuthService.hash_password("password123")
    mock_user_repo.find_by_email.return_value = {
        "id": "user123",
        "hashed_password": hashed_password,
        "is_active": True
    }
    
    user = await auth_service.authenticate_user("test@example.com", "wrongpassword")
    
    assert user is None


def test_token_generation_and_validation(auth_service):
    user_id = "user123"
    
    access_token = AuthService.create_access_token({"sub": user_id})
    refresh_token = AuthService.create_refresh_token({"sub": user_id})
    
    access_payload = AuthService.decode_token(access_token)
    refresh_payload = AuthService.decode_token(refresh_token)
    
    assert access_payload["sub"] == user_id
    assert access_payload["type"] == "access"
    assert refresh_payload["sub"] == user_id
    assert refresh_payload["type"] == "refresh"


def test_password_hashing():
    password = "testpassword123"
    hashed = AuthService.hash_password(password)
    
    assert hashed != password
    assert AuthService.verify_password(password, hashed)
    assert not AuthService.verify_password("wrongpassword", hashed)
