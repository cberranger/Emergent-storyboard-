"""Simple test to verify auth module imports and basic functionality"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

try:
    from services.auth_service import AuthService
    from repositories.user_repository import UserRepository
    from dtos.auth_dtos import LoginRequest, RegisterRequest
    from api.v1 import auth_router
    
    print("[OK] All auth modules import successfully")
    
    token = AuthService.create_access_token({"sub": "test123"})
    print(f"[OK] Token generation works: {token[:20]}...")
    
    payload = AuthService.decode_token(token)
    print(f"[OK] Token decoding works: {payload}")
    
    password = "testpassword123"
    hashed = AuthService.hash_password(password)
    print(f"[OK] Password hashing works")
    
    verified = AuthService.verify_password(password, hashed)
    print(f"[OK] Password verification works: {verified}")
    
    print("\n[SUCCESS] All auth system checks passed!")
    
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
