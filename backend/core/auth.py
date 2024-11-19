from datetime import datetime, timedelta
from typing import Optional
from django.conf import settings
from django.contrib.auth import get_user_model
from jose import JWTError, jwt
from ninja.security import HttpBearer
from .schemas import TokenPayload
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            logger.debug(f"Attempting to decode token: {token}")
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=["HS256"]
            )
            logger.debug(f"Decoded payload: {payload}")
            
            # Convert sub back to int for database lookup
            user_id = int(payload["sub"])
            exp = payload["exp"]
            
            if datetime.fromtimestamp(exp) < datetime.now():
                logger.debug("Token has expired")
                return None
                
            user = User.objects.filter(id=user_id).first()
            if user is None:
                logger.debug(f"No user found with id: {user_id}")
                return None
                
            logger.debug(f"Successfully authenticated user: {user.username}")
            return user
            
        except (JWTError, ValueError) as e:
            logger.debug(f"JWT Error: {str(e)}")
            return None
        except Exception as e:
            logger.debug(f"Unexpected error: {str(e)}")
            return None

def create_access_token(*, user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.NINJA_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds() / 60
        )
    
    to_encode = {
        "exp": int(expire.timestamp()),
        "sub": str(user_id)  # Convert user_id to string
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    
    return encoded_jwt

def create_refresh_token(*, user_id: int) -> str:
    expire = datetime.utcnow() + settings.NINJA_JWT['REFRESH_TOKEN_LIFETIME']
    to_encode = {
        "exp": int(expire.timestamp()),
        "sub": str(user_id)  # Convert user_id to string
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    
    return encoded_jwt
