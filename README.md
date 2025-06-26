# CarWatch Backend API

An optimized, production-ready Flask backend service for vehicle license plate recognition and tracking using YOLOv8 models. Features automatic license plate detection, OCR character recognition, user management, and comprehensive vehicle tracking capabilities.

## 🚀 Features

- 🚗 **License Plate Detection**: Automatic detection using optimized YOLOv8 models
- 🔍 **OCR Recognition**: Real-time character recognition with confidence scoring
- 👤 **User Management**: Complete authentication system with secure session handling
- 📊 **History Tracking**: Vehicle entry/exit logging with user association
- 🔒 **Secure Authentication**: bcrypt password hashing with configurable rounds
- 🐳 **Production Optimized**: Gunicorn WSGI server with memory-efficient configuration
- 📁 **Image Processing**: BLOB storage and JPEG conversion utilities
- 🛡️ **Input Sanitization**: Comprehensive input validation and cleaning
- 📝 **Structured Logging**: Rotating logs with configurable levels

## 📁 Project Structure 

```
carwatch-backend/
├── app/                        # Main application package
│   ├── __init__.py            # Application factory
│   ├── config.py              # Configuration management
│   ├── routes/                # Route blueprints
│   │   ├── __init__.py
│   │   ├── main.py           # Health check & info routes
│   │   ├── auth.py           # Authentication endpoints
│   │   └── history.py        # OCR & history endpoints
│   ├── services/              # Business logic layer
│   │   ├── __init__.py
│   │   ├── ocr_service.py    # Optimized YOLO-based OCR
│   │   └── db_upload.py      # Image database upload service
│   └── utils/                 # Utility modules
│       ├── __init__.py
│       ├── database.py       # Database connection management
│       ├── auth.py           # Authentication helpers
│       ├── blob_utils.py     # BLOB to image conversion
│       └── logging_config.py # Logging configuration
├── models/                    # YOLO model files (*.pt)
│   ├── best_LPD.pt           # License Plate Detection model
│   ├── best_OCR.pt           # Character Recognition model
│   └── README.md             # Model documentation
├── logs/                      # Application logs
├── uploads/                   # Temporary image storage
├── images/                    # Processed image output
├── wsgi.py                   # Optimized WSGI entry point
├── gunicorn.conf.py         # Production server configuration
├── requirements.txt          # Pinned Python dependencies
├── .env                      # Environment variables
├── .gitignore               # Git ignore rules
└── README.md                # This documentation
```

## 🔧 Prerequisites

- **Python**: 3.8 or higher
- **Database**: MySQL 5.7+ or MariaDB 10.3+
- **Models**: YOLOv8 model files (`best_LPD.pt`, `best_OCR.pt`)

## 📚 Additional Documentation

- 🤖 **[Model Documentation](models/README.md)** - Detailed information about YOLO models, training metrics, and performance examples
- 🐧 **[Ubuntu Setup Guide](Ubuntu_setup.md)** - Complete Ubuntu/Linux installation and configuration guide

## ⚡ Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/carwatch-backend.git
cd carwatch-backend
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Create .env file with your configuration
# Use the example below as template
```

**Environment Variables (.env):**
```env
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_database_password
DB_NAME=carwatch
DB_PORT=3306

# Security Settings
SECRET_KEY=your_secret_key_here
BCRYPT_ROUNDS=12

# Application Settings
DEBUG=False
```

### 5. Set Up Database

**Import the provided SQL file:**
```bash
# Import the complete database structure and procedures
mysql -u root -p < "carwatch database.sql"
```

**Database Structure:**
The SQL file creates the complete `carwatch` database with the following tables:

- **`users`** - User authentication and management
  - `user_id` (Primary Key, Auto Increment)
  - `username` (Unique, Not Null)
  - `password` (bcrypt hashed)
  - `created_at` (Timestamp)

- **`history`** - Vehicle tracking records
  - `history_id` (Primary Key, Auto Increment)
  - `plate` (License plate number)
  - `subject` (Entry/Exit status)
  - `description` (Car being used / Car is available)
  - `date` (Timestamp)
  - `user_id` (Foreign Key, nullable)
  - `image_id` (Foreign Key to images table)

- **`images`** - BLOB storage for processed images
  - `image_id` (Primary Key, Auto Increment)
  - `filename` (Image filename)
  - `image_data` (MEDIUMBLOB - binary image data)
  - `file_size` (File size in bytes)
  - `file_type` (Image format)
  - `upload_date` (Timestamp)

**Stored Procedures:**
- `clear_old_data(weeks_to_keep)` - Cleanup procedure for old history records

### 6. Add Model Files
```bash
# Place your YOLO model files in the models directory
cp your_best_LPD.pt models/best_LPD.pt
cp your_best_OCR.pt models/best_OCR.pt
```

> 📋 **For detailed model information, training metrics, and performance examples, see [models/README.md](models/README.md)**

### 7. Run Application
```bash
# Development mode
python wsgi.py

# Production mode
gunicorn --config gunicorn.conf.py wsgi:app
```

## 🌐 API Documentation

### Base URL
- Development: `http://localhost:8000`
- Production: `http://your-domain.com`

### System Endpoints

#### Health Check
```http
GET /health
```

**Response:**
```json
{
    "status": "healthy",
    "service": "carwatch-backend",
    "endpoints": {
        "auth": "/auth/*",
        "api": "/api/*"
    }
}
```

#### API Information
```http
GET /
```

**Response:**
```json
{
    "message": "CarWatch Backend API is running",
    "version": "1.0.0",
    "status": "healthy"
}
```

### Authentication Endpoints

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

**Response:**
```json
{
    "success": true,
    "message": "User registered successfully"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Login successful",
    "data": {
        "user_id": 1,
        "username": "your_username"
    }
}
```

#### Get Current User
```http
GET /auth/me
```

**Response:**
```json
{
    "success": true,
    "data": {
        "user_id": 1,
        "username": "your_username"
    }
}
```

#### Update Username
```http
POST /auth/update/username
Content-Type: application/json

{
    "new_username": "new_username"
}
```

#### Update Password
```http
POST /auth/update/password
Content-Type: application/json

{
    "current_password": "current_password",
    "new_password": "new_password",
    "confirm_new_password": "new_password"
}
```

#### Delete User Account
```http
POST /auth/delete
Content-Type: application/json

{
    "password": "user_password"
}
```

#### Logout
```http
POST /auth/logout
```

### OCR & History Endpoints

#### Upload Image for OCR Processing
```http
POST /api/upload_image?status=entering
Content-Type: multipart/form-data

Form Data:
- image: [image file]
```

**Parameters:**
- `status`: `entering` | `leaving` | `unknown`

**Response:**
```json
{
    "success": true,
    "message": "Image received, uploaded to database, OCR processed, and data recorded successfully.",
    "plate_number": "ABC123",
    "status": "entering",
    "image_uploaded": true,
    "image_filename": "image_20250615123456789.jpg"
}
```

#### Get History Records
```http
GET /api/history
```

**Response:**
```json
{
    "success": true,
    "message": "History retrieved",
    "data": [
        {
            "subject": "Vehicle Entry",
            "plate": "ABC123",
            "description": "car is available",
            "date": "2025-06-15T10:30:00",
            "username": "user123"
        }
    ]
}
```

#### Manual Plate Record
```http
POST /api/plate
Content-Type: application/json

{
    "plate": "XYZ789",
    "subject": "Manual Entry",
    "description": "Manually recorded plate"
}
```

#### Fetch Latest Image from Database
```http
GET /api/fetch_img
```

**Response:**
Returns raw JPEG binary data with appropriate headers.

**Headers:**
- `Content-Type: image/jpeg`
- `Content-Length: [image_size_bytes]`
- `Cache-Control: no-cache`

**Error Response:**
```json
{
    "success": false,
    "message": "No images found in database"
}
```

#### Cleanup Old Images
```http
POST /api/cleanup_images?max_age_hours=24
```

**Parameters:**
- `max_age_hours`: Maximum age in hours for keeping temporary images (default: 24)

**Response:**
```json
{
    "success": true,
    "message": "Cleanup completed. Removed 3 old image(s)",
    "cleaned_files": 3
}
```

## 📝 API Status & Future Development

**Note**: Some API endpoints are included for future development needs and may not be actively used in the current implementation. These endpoints are maintained for potential feature expansion and system extensibility.

**Currently Active Endpoints:**
- Health check and system status
- User authentication (login/logout)
- User registration and account management
- Username/password updates
- Account deletion
- Image upload and OCR processing
- Basic history retrieval
- Image fetching from database

**Future Development Endpoints:**
- Advanced history filtering
- Comprehensive user management features
- Automated/Manual image cleanup scheduling for certain timing

## ⚙️ Configuration

### Gunicorn Configuration (Production Optimized)

The `gunicorn.conf.py` file contains optimized settings for production:

```python
# Optimized for memory efficiency and performance
workers = min(cpu_count * 2 + 1, 4)  # Capped at 4 workers
worker_class = "gthread"             # Threading for ML workloads
threads = 2                          # 2 threads per worker
timeout = 180                        # Increased for ML processing
max_requests = 100                   # Worker recycling for memory
preload_app = True                   # Reduces memory usage
```

**Key Optimizations:**
- **Memory Efficient**: Threading instead of multiprocessing
- **ML Optimized**: Preloaded models reduce startup time
- **Auto-Recovery**: Worker recycling prevents memory leaks
- **Resource Capped**: Maximum 4 workers to prevent resource exhaustion

### Dependencies (Pinned Versions)

```txt
Flask==3.0.0                    # Web framework
mysql-connector-python==8.2.0   # Database connector
bcrypt==4.1.2                   # Password hashing
bleach==6.1.0                   # Input sanitization
opencv-python==4.10.0.84        # Computer vision (full version)
numpy==1.26.2                   # Numerical computing
ultralytics==8.0.225            # YOLOv8 models
gunicorn==21.2.0                # WSGI server
python-dotenv==1.0.0            # Environment variables
Pillow==10.1.0                  # Image processing
```

## 🔄 OCR Processing Flow

1. **Image Upload**: Client uploads image via `/api/upload_image`
2. **Temporary Storage**: Image saved temporarily to `uploads/` directory
3. **Database Storage**: Image converted and stored as BLOB in `images` table
4. **License Plate Detection**: YOLOv8 LPD model detects plates (conf=0.5, iou=0.5)
5. **Plate Cropping**: Best confidence plate cropped with 10px padding
6. **Character Recognition**: OCR model recognizes characters (conf=0.1, iou=0.3)
7. **Text Assembly**: Characters sorted by x-position to form plate number
8. **History Storage**: Results stored in `history` table with user association
9. **Cleanup**: Temporary files automatically removed
10. **Response**: Processed results returned to client

### Image Fetching Flow
1. **Request**: Client calls `GET /api/fetch_img`
2. **Database Query**: Latest image retrieved directly from database
3. **Binary Response**: Raw JPEG data returned with appropriate headers
4. **No Caching**: Each request fetches fresh data from database

### Performance Metrics
- **Processing Speed**: ~20-30% faster than previous version
- **Memory Usage**: ~30-40% reduction through optimization
- **Model Loading**: Single load per worker (preload_app=True)
- **File Handling**: Immediate cleanup prevents storage bloat
- **Image Fetching**: Direct binary response eliminates file system operations

## 🧪 Testing

### Basic API Testing

```bash
# Test health endpoint
curl -X GET http://localhost:8000/health

# Test OCR upload
curl -X POST -F "image=@test_image.jpg" \
     "http://localhost:8000/api/upload_image?status=entering"

# Test image fetching (returns binary JPEG data)
curl -X GET http://localhost:8000/api/fetch_img --output latest_image.jpg

# Test image cleanup
curl -X POST "http://localhost:8000/api/cleanup_images?max_age_hours=24"
```

## 🚀 Deployment

### Production Deployment

1. **Server Setup**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install dependencies
   sudo apt install python3 python3-pip python3-venv mysql-server nginx -y
   ```

2. **Application Setup**
   ```bash
   # Clone and setup
   git clone https://github.com/yourusername/carwatch-backend.git
   cd carwatch-backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   # Create production environment file
   cp .env.example .env
   nano .env
   ```

4. **Create Systemd Service**
   ```ini
   # /etc/systemd/system/carwatch.service
   [Unit]
   Description=CarWatch Backend API
   After=network.target mysql.service
   
   [Service]
   Type=notify
   User=www-data
   Group=www-data
   RuntimeDirectory=carwatch
   WorkingDirectory=/opt/carwatch-backend
   Environment=PATH=/opt/carwatch-backend/venv/bin
   ExecStart=/opt/carwatch-backend/venv/bin/gunicorn --config gunicorn.conf.py wsgi:app
   ExecReload=/bin/kill -s HUP $MAINPID
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

5. **Nginx Configuration**
   ```nginx
   # /etc/nginx/sites-available/carwatch
   server {
       listen 80;
       server_name your-domain.com;
       
       client_max_body_size 20M;
       
       location / {
           proxy_pass http://127.0.0.1:9036;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_connect_timeout 300s;
           proxy_read_timeout 300s;
       }
       
       location /static {
           alias /opt/carwatch-backend/static;
           expires 1y;
           add_header Cache-Control "public, immutable";
       }
   }
   ```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p logs uploads models images

# Non-root user for security
RUN useradd -m -u 1000 carwatch && chown -R carwatch:carwatch /app
USER carwatch

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  carwatch-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=mysql
      - DB_USER=carwatch
      - DB_PASSWORD=secure_password
      - DB_NAME=carwatch
    volumes:
      - ./models:/app/models
      - logs:/app/logs
    depends_on:
      - mysql
    restart: unless-stopped
    
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: carwatch
      MYSQL_USER: carwatch
      MYSQL_PASSWORD: secure_password
    volumes:
      - mysql_data:/var/lib/mysql
    restart: unless-stopped

volumes:
  mysql_data:
  logs:
```

---

**Version**: 1.2.0 (Optimized & Simplified)  
**Last Updated**: June 26, 2025  
**Maintainer**: CarWatch Development Team  
**Description**: Production-ready Flask backend for vehicle license plate recognition and tracking using YOLOv8 models with comprehensive authentication and history management.
