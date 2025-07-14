from datetime import datetime, timedelta, UTC
from litestar import Router, post, get, Request
from litestar.exceptions import HTTPException
from app.models import User
from app.schemas import UserCreate, UserLogin, UserResponse, Token, MessageResponse
from app.auth import get_password_hash, verify_password, create_access_token, generate_secure_token
from app.email_service import email_service
from app.dependencies import get_db_session


@post("/signup")
async def signup(request: Request) -> dict:
    """Client user signup with email verification"""
    # Parse request body
    body = await request.json()
    user_data = UserCreate(**body)
    
    if user_data.user_type != "client":
        raise HTTPException(detail="Only client users can sign up through this endpoint", status_code=400)
    
    db = get_db_session(request)
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(detail="User with this email or username already exists", status_code=400)
    
    # Create verification token
    verification_token = generate_secure_token()
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        user_type=user_data.user_type,
        is_verified=False
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Send verification email
    base_url = str(request.base_url).rstrip('/')
    email_service.send_verification_email(user.email, verification_token, base_url)
    
    # Store verification token
    # For simplicity, we'll store it in memory
    if not hasattr(request.app.state, 'verification_tokens'):
        request.app.state.verification_tokens = {}
    
    request.app.state.verification_tokens[user.email] = {
        'token': verification_token,
        'expires_at': datetime.now(UTC) + timedelta(hours=24)
    }
    
    return {
        "message": "User created successfully. Please check your email for verification.",
        "user_id": user.id
    }


@post("/login")
async def login(request: Request) -> Token:
    """User login"""
    # Parse request body
    body = await request.json()
    user_data = UserLogin(**body)
    
    db = get_db_session(request)
    
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(detail="Incorrect email or password", status_code=401)
    
    # For client users, check if email is verified
    if user.user_type == "client" and not user.is_verified:
        raise HTTPException(detail="Please verify your email before logging in", status_code=401)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.email, "user_type": user.user_type}
    )
    
    return Token(access_token=access_token, token_type="bearer")


@get("/verify-email")
async def verify_email(email: str, token: str, request: Request) -> MessageResponse:
    """Verify user email"""
    db = get_db_session(request)
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(detail="User not found", status_code=404)
    
    if user.is_verified:
        return MessageResponse(message="Email already verified")
    
    # Check verification token
    if not hasattr(request.app.state, 'verification_tokens'):
        raise HTTPException(detail="Invalid verification token", status_code=400)
    
    stored_data = request.app.state.verification_tokens.get(email)
    if not stored_data:
        raise HTTPException(detail="Invalid verification token", status_code=400)
    
    if stored_data['token'] != token:
        raise HTTPException(detail="Invalid verification token", status_code=400)
    
    if datetime.now(UTC) > stored_data['expires_at']:
        # Clean up expired token
        del request.app.state.verification_tokens[email]
        raise HTTPException(detail="Verification token expired", status_code=400)
    
    # Mark user as verified
    user.is_verified = True
    db.commit()
    
    # Clean up token
    del request.app.state.verification_tokens[email]
    
    return MessageResponse(message="Email verified successfully")


# Ops user creation (for development/testing)
@post("/create-ops-user")
async def create_ops_user(request: Request) -> dict:
    """Create Ops user (for development/testing purposes)"""
    # Parse request body
    body = await request.json()
    user_data = UserCreate(**body)
    
    if user_data.user_type != "ops":
        raise HTTPException(detail="This endpoint is for creating Ops users only", status_code=400)
    
    db = get_db_session(request)
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(detail="User with this email or username already exists", status_code=400)
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        user_type=user_data.user_type,
        is_verified=True  # Ops users are automatically verified
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {
        "message": "Ops user created successfully",
        "user_id": user.id
    }


auth_router = Router(path="/auth", route_handlers=[signup, login, verify_email, create_ops_user])
