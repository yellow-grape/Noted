from datetime import datetime, timedelta
from typing import Optional
from django.conf import settings
from django.contrib.auth import get_user_model
from jose import JWTError, jwt
from ninja.security import HttpBearer
from .schemas import TokenPayload

User = get_user_model()

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=["HS256"]
            )
            token_data = TokenPayload(**payload)
            
            if datetime.fromtimestamp(token_data.exp) < datetime.now():
                return None
                
            user = User.objects.filter(id=token_data.sub).first()
            if user is None:
                return None
                
            return user
            
        except JWTError:
            return None

def create_access_token(*, user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.NINJA_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds() / 60
        )
    
    to_encode = {"exp": expire, "sub": user_id}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    
    return encoded_jwt

def create_refresh_token(*, user_id: int) -> str:
    expire = datetime.utcnow() + settings.NINJA_JWT['REFRESH_TOKEN_LIFETIME']
    to_encode = {"exp": expire, "sub": user_id}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    
    return encoded_jwt
