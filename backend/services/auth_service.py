from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from repositories.user_repository import UserRepository
from config import config
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = config.JWT_SECRET_KEY
ALGORITHM = config.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = config.JWT_REFRESH_TOKEN_EXPIRE_DAYS


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    async def register_user(
        self,
        email: str,
        username: str,
        password: str
    ) -> Dict[str, Any]:
        existing_email = await self.user_repository.find_by_email(email)
        if existing_email:
            raise ValueError("Email already registered")
        
        existing_username = await self.user_repository.find_by_username(username)
        if existing_username:
            raise ValueError("Username already taken")
        
        user_doc = {
            "id": str(uuid.uuid4()),
            "email": email.lower(),
            "username": username.lower(),
            "hashed_password": self.hash_password(password),
            "api_keys": {
                "runpod": None,
                "openai": None,
                "civitai": None
            },
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await self.user_repository.create(user_doc)
        
        user_doc.pop("hashed_password")
        return user_doc
    
    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        user = await self.user_repository.find_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user["hashed_password"]):
            return None
        if not user.get("is_active", True):
            return None
        
        user.pop("hashed_password")
        return user
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        user = await self.user_repository.find_by_id(user_id)
        if user:
            user.pop("hashed_password", None)
        return user
    
    async def update_user_api_keys(
        self,
        user_id: str,
        api_keys: Dict[str, Optional[str]]
    ) -> Optional[Dict[str, Any]]:
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            return None
        
        current_keys = user.get("api_keys", {})
        
        for key_name in ["runpod", "openai", "civitai"]:
            if key_name in api_keys and api_keys[key_name] is not None:
                current_keys[key_name] = api_keys[key_name]
        
        updated_user = await self.user_repository.update_api_keys(user_id, current_keys)
        if updated_user:
            updated_user.pop("hashed_password", None)
        return updated_user
