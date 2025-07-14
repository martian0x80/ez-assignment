from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database Configuration
    database_url: str = "postgresql://fileuser:filepass@localhost:5432/file_sharing_db"
    
    # Security Configuration
    secret_key: str = "your-secret-key-here-make-it-long-and-random"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # File Storage Configuration
    upload_dir: str = "uploads"
    max_file_size: int = 10485760  # 10MB in bytes
    
    # Email Configuration
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # Application Configuration
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Allowed file extensions for Ops Users
    allowed_extensions: set = {".pptx", ".docx", ".xlsx"}
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Create upload directory if it doesn't exist
os.makedirs(settings.upload_dir, exist_ok=True)
