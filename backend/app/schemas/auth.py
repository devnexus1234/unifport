from pydantic import BaseModel
from typing import Optional, Dict, Any

class LoginRequest(BaseModel):
    username: str
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    user: Dict[str, Any]

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    email: Optional[str] = None

