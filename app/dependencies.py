from typing import Optional
from litestar import Request
from litestar.exceptions import NotAuthorizedException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import verify_token
from app.models import User
from app.schemas import TokenData


def get_current_user(request: Request) -> User:
    """Get current authenticated user"""
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise NotAuthorizedException("Invalid authorization header")
    
    token = authorization.split(" ")[1]
    token_data = verify_token(token)
    
    if not token_data:
        raise NotAuthorizedException("Invalid token")
    
    db = next(get_db())
    user = db.query(User).filter(User.email == token_data.email).first()
    
    if not user:
        raise NotAuthorizedException("User not found")
    
    return user


def get_current_ops_user(request: Request) -> User:
    """Get current authenticated Ops user"""
    user = get_current_user(request)
    if user.user_type != "ops":
        raise NotAuthorizedException("Access denied. Ops user required.")
    return user


def get_current_client_user(request: Request) -> User:
    """Get current authenticated Client user"""
    user = get_current_user(request)
    if user.user_type != "client":
        raise NotAuthorizedException("Access denied. Client user required.")
    if not user.is_verified:
        raise NotAuthorizedException("Email verification required.")
    return user


def get_db_session(request: Request) -> Session:
    """Get database session"""
    return next(get_db())
