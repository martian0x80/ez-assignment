# EZ Assignment - Secure File Sharing System

A secure file-sharing system built with Python, Litestar framework, and PostgreSQL. The system supports two types of users with different permissions and provides secure file upload/download functionality.

## Features

### User Types
- **Ops Users**: Can upload files (only .pptx, .docx, .xlsx)
- **Client Users**: Can download files and list all uploaded files

### Security Features
- JWT-based authentication
- Role-based access control
- Email verification for client users
- Secure encrypted download URLs
- File type validation
- File size limits

## Tech Stack

- **Framework**: Litestar (Python)
- **Database**: PostgreSQL
- **Authentication**: JWT tokens
- **File Storage**: Local filesystem
- **Email**: SMTP (configurable)
- **Testing**: pytest

## Prerequisites

- Python 3.12+
- PostgreSQL
- pip

## Installation

### Option 1: Using UV (Recommended)

1. **Install UV** (if not already installed)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd EZAssignment
   ```

3. **Install dependencies with UV**
   ```bash
   uv sync
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Set up PostgreSQL database**
   ```bash
   # Create database
   createdb file_sharing_db
   
   # Run migrations
   uv run alembic upgrade head
   ```

6. **Run the application**
   ```bash
   uv run python -m app.main
   ```

### Option 2: Using pip (Fallback)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd EZAssignment
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Set up PostgreSQL database**
   ```bash
   # Create database
   createdb file_sharing_db
   
   # Run migrations
   alembic upgrade head
   ```

6. **Run the application**
   ```bash
   python -m app.main
   ```

## Configuration

Edit the `.env` file with your settings:

```env
# Database Configuration
DATABASE_URL=postgresql://fileuser:filepass@localhost:5432/file_sharing_db

# Security Configuration
SECRET_KEY=your-secret-key-here-make-it-long-and-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Storage Configuration
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760  # 10MB in bytes

# Email Configuration (for verification emails)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Application Configuration
DEBUG=true
HOST=0.0.0.0
PORT=8000
```

## API Documentation

### Authentication Endpoints

#### 1. Client User Signup
```http
POST /auth/signup
Content-Type: application/json

{
  "email": "client@example.com",
  "username": "clientuser",
  "password": "password123",
  "user_type": "client"
}
```

#### 2. User Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

#### 3. Email Verification
```http
GET /auth/verify-email?email=user@example.com&token=verification_token
```

#### 4. Create Ops User (Development)
```http
POST /auth/create-ops-user
Content-Type: application/json

{
  "email": "ops@example.com",
  "username": "opsuser",
  "password": "password123",
  "user_type": "ops"
}
```

### File Management Endpoints

#### 1. Upload File (Ops Users Only)
```http
POST /files/upload
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data

file: <file_upload>
```

#### 2. List Files (Client Users Only)
```http
GET /files/list
Authorization: Bearer <jwt_token>
```

#### 3. Get Download Link (Client Users Only)
```http
GET /files/download/{file_id}
Authorization: Bearer <jwt_token>
```

#### 4. Download File (Using Secure Token)
```http
GET /files/download-file/{token}
```

## Usage Examples

### 1. Create a Client User and Verify Email

```bash
# Sign up
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client@example.com",
    "username": "clientuser",
    "password": "password123",
    "user_type": "client"
  }'

# Check console for verification token (in development)
# Verify email
curl "http://localhost:8000/auth/verify-email?email=client@example.com&token=VERIFICATION_TOKEN"
```

### 2. Create an Ops User

```bash
curl -X POST http://localhost:8000/auth/create-ops-user \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ops@example.com",
    "username": "opsuser",
    "password": "password123",
    "user_type": "ops"
  }'
```

### 3. Login and Get Token

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ops@example.com",
    "password": "password123"
  }'
```

### 4. Upload File (Ops User)

```bash
curl -X POST http://localhost:8000/files/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@document.docx"
```

### 5. List Files (Client User)

```bash
curl -X GET http://localhost:8000/files/list \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 6. Get Download Link (Client User)

```bash
curl -X GET http://localhost:8000/files/download/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 7. Download File

```bash
curl -X GET "http://localhost:8000/files/download-file/YOUR_DOWNLOAD_TOKEN" \
  --output downloaded_file.docx
```

## Database Migrations

### Using UV
```bash
# Create a new migration
uv run alembic revision --autogenerate -m "Description of changes"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```

### Using pip
```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```


## Production Deployment

### 1. Environment Setup

1. **Use a production database**
   - Set up PostgreSQL on a dedicated server
   - Use connection pooling (e.g., PgBouncer)
   - Configure proper backups

2. **Security Configuration**
   - Generate a strong SECRET_KEY
   - Use HTTPS in production
   - Configure proper CORS settings
   - Set DEBUG=false

3. **File Storage**
   - Consider using cloud storage (AWS S3, Google Cloud Storage)
   - Implement file cleanup for unused files
   - Set up proper backup strategies

### 2. Deployment Options

#### Option A: Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "app.main"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/file_sharing_db
    depends_on:
      - db
    volumes:
      - ./uploads:/app/uploads

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=file_sharing_db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### Option B: Traditional Server Deployment

1. **Set up a production server** (Ubuntu/CentOS)
2. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip postgresql nginx
   ```

3. **Configure Nginx** as reverse proxy:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **Use Gunicorn** for production:
   ```bash
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

5. **Set up systemd service**:
   ```ini
   [Unit]
   Description=File Sharing System
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/path/to/your/app
   Environment=PATH=/path/to/your/venv/bin
   ExecStart=/path/to/your/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

### 3. Monitoring and Logging

1. **Set up logging**:
   - Configure structured logging
   - Set up log rotation
   - Monitor application logs

2. **Health checks**:
   - Implement health check endpoints
   - Set up monitoring (Prometheus, Grafana)

3. **Error tracking**:
   - Integrate with error tracking services (Sentry)

### 4. Security Considerations

1. **HTTPS**: Use SSL/TLS certificates (Let's Encrypt)
2. **Rate limiting**: Implement API rate limiting
3. **Input validation**: Validate all inputs
4. **File scanning**: Scan uploaded files for malware
5. **Access logs**: Monitor and log access patterns

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `make test`
6. Run quality checks: `make lint format type-check`
7. Submit a pull request

## License

This project is licensed under the Unlicense. 