import os
import uuid
from datetime import datetime, timedelta, UTC
from typing import List
from litestar import Router, post, get, Request
from litestar.exceptions import HTTPException
from litestar.datastructures import UploadFile
from sqlalchemy.orm import Session
from app.models import User, File, DownloadToken
from app.schemas import FileResponse, FileListResponse, DownloadTokenResponse, MessageResponse
from app.auth import generate_secure_token
from app.config import settings
from app.dependencies import get_current_ops_user, get_current_client_user, get_db_session


@post("/upload")
async def upload_file(
    request: Request
) -> MessageResponse:
    """Upload file (Ops users only)"""
    # Get current user
    current_user = get_current_ops_user(request)
    
    # Parse multipart form data
    form = await request.form()
    file = form.get("file")
    
    if not file or not hasattr(file, 'filename'):
        raise HTTPException(detail="No file provided", status_code=400)
    
    # Check file extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in settings.allowed_extensions:
        raise HTTPException(
            detail=f"Only {', '.join(settings.allowed_extensions)} files are allowed",
            status_code=400
        )
    
    # Check file size
    # if file.size > settings.max_file_size:
    #     raise HTTPException(
    #         detail=f"File size exceeds maximum limit of {settings.max_file_size} bytes",
    #         status_code=400
    #     )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.upload_dir, unique_filename)
    
    # Save file
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(detail=f"Failed to save file: {str(e)}", status_code=500)
    
    # Save file record to database
    db = get_db_session(request)
    file_record = File(
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=0,
        file_type=file_extension,
        uploader_id=current_user.id
    )
    
    db.add(file_record)
    db.commit()
    db.refresh(file_record)
    
    return MessageResponse(message=f"File uploaded successfully. File ID: {file_record.id}")


@get("/list")
async def list_files(
    request: Request
) -> FileListResponse:
    """List all uploaded files (Client users only)"""
    db = get_db_session(request)
    
    files = db.query(File).order_by(File.created_at.desc()).all()
    
    file_responses = []
    for file in files:
        file_responses.append(FileResponse(
            id=file.id,
            filename=file.filename,
            original_filename=file.original_filename,
            file_size=file.file_size,
            file_type=file.file_type,
            uploader_id=file.uploader_id,
            created_at=file.created_at
        ))
    
    return FileListResponse(files=file_responses, total=len(file_responses))


@get("/download/{file_id:int}")
async def get_download_link(
    file_id: int,
    request: Request
) -> DownloadTokenResponse:
    """Get secure download link for a file (Client users only)"""
    # Get current user
    current_user = get_current_client_user(request)
    
    db = get_db_session(request)
    
    # Check if file exists
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(detail="File not found", status_code=404)
    
    # Generate secure download token
    download_token = generate_secure_token()
    
    # Create download token record
    token_record = DownloadToken(
        token=download_token,
        file_id=file_id,
        client_id=current_user.id,
        expires_at=datetime.now(UTC) + timedelta(hours=1)  # Token expires in 1 hour
    )
    
    db.add(token_record)
    db.commit()
    
    # Create download link
    base_url = str(request.base_url).rstrip('/')
    download_link = f"{base_url}/files/download-file/{download_token}"
    
    return DownloadTokenResponse(
        download_link=download_link,
        message="success"
    )


@get("/download-file/{token:str}")
async def download_file(
    token: str,
    request: Request
) -> bytes:
    """Download file using secure token"""
    db = get_db_session(request)
    
    # Find download token
    token_record = db.query(DownloadToken).filter(
        DownloadToken.token == token,
        DownloadToken.is_used == False,
        DownloadToken.expires_at > datetime.now(UTC)
    ).first()
    
    if not token_record:
        raise HTTPException(detail="Invalid or expired download token", status_code=400)
    
    # Get file
    file = db.query(File).filter(File.id == token_record.file_id).first()
    if not file:
        raise HTTPException(detail="File not found", status_code=404)
    
    # Check if file exists on disk
    if not os.path.exists(file.file_path):
        raise HTTPException(detail="File not found on server", status_code=404)
    
    # Mark token as used
    token_record.is_used = True
    db.commit()
    
    # Read and return file
    try:
        with open(file.file_path, "rb") as f:
            content = f.read()
        
        # Set response headers for file download
        request.response.headers["Content-Disposition"] = f"attachment; filename={file.original_filename}"
        request.response.headers["Content-Type"] = "application/octet-stream"
        
        return content
    except Exception as e:
        raise HTTPException(detail=f"Failed to read file: {str(e)}", status_code=500) from e

files_router = Router(path="/files", route_handlers=[upload_file, list_files, get_download_link, download_file])
