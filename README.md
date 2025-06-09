# CarWatch Backend API

A comprehensive Flask-based backend service for vehicle license plate recognition and tracking system using YOLOv8 models. This system provides automatic license plate detection, OCR character recognition, user management, and vehicle tracking capabilities.

## 🚀 Features

- 🚗 **License Plate Detection**: Automatic detection using YOLOv8 models
- 🔍 **OCR Recognition**: Real-time character recognition on detected plates
- 👤 **User Management**: Complete authentication system with registration/login
- 📊 **History Tracking**: Vehicle entry/exit logging with timestamps
- 🔒 **Secure Authentication**: Password hashing with bcrypt and session management
- 🐳 **Production Ready**: Gunicorn WSGI server with optimized configuration
- 📁 **File Upload**: Image processing with temporary storage
- 🛡️ **Input Sanitization**: Bleach-based input cleaning for security
- 📝 **Comprehensive Logging**: Structured logging with rotation

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
│   │   └── ocr_service.py    # YOLO-based OCR processing
│   └── utils/                 # Utility modules
│       ├── __init__.py
│       ├── database.py       # Database connection management
│       ├── auth.py           # Authentication helpers
│       └── logging_config.py # Logging configuration
├── models/                    # YOLO model files (*.pt)
│   ├── best_LPD.pt           # License Plate Detection model
│   ├── best_OCR.pt           # Character Recognition model
│   └── README.md             # Model documentation
├── logs/                      # Application logs
├── uploads/                   # Temporary image storage
├── wsgi.py                   # WSGI entry point
├── gunicorn.conf.py         # Production server configuration
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
└── README.md                # This documentation
```

## 🔧 Prerequisites

- **Python**: 3.8 or higher
- **Database**: MySQL 5.7+ or MariaDB 10.3+
- **Models**: YOLOv8 model files (`best_LPD.pt`, `best_OCR.pt`)
- **Memory**: Minimum 2GB RAM (4GB+ recommended for OCR processing)
- **Storage**: 1GB+ free space for logs and temporary files

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
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
nano .env  # or use your preferred editor
```

### 5. Set Up Database
```sql
-- Create database
CREATE DATABASE carwatch;

-- Create users table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create history table
CREATE TABLE history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plate VARCHAR(255),
    subject VARCHAR(255),
    description TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);
```

### 6. Add Model Files
```bash
# Place your YOLO model files in the models directory
cp your_best_LPD.pt models/best_LPD.pt
cp your_best_OCR.pt models/best_OCR.pt
```

### 7. Initialize Application
```bash
python start.py
```

### 8. Run Application
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

**Response:**
```json
{
    "success": true,
    "message": "Username updated successfully",
    "data": {
        "new_username": "new_username"
    }
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

**Response:**
```json
{
    "success": true,
    "message": "Password updated successfully"
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

**Response:**
```json
{
    "success": true,
    "message": "Account deleted successfully"
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
    "message": "Image received, OCR processed, and data recorded successfully.",
    "plate_number": "ABC123",
    "status": "entering"
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
            "date": "2024-01-15T10:30:00"
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

#### List All Endpoints
```http
GET /endpoints
```

**Response:**
```json
{
    "endpoints": [
        {
            "endpoint": "/",
            "methods": ["GET"],
            "blueprint": "main"
        }
    ]
}
```

## ⚙️ Configuration

### Environment Variables (.env)

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

### Gunicorn Configuration

The `gunicorn.conf.py` file contains production-optimized settings:

- **Workers**: Optimized for single-core VPS
- **Threading**: 4 threads per worker
- **Timeout**: 120 seconds for ML processing
- **Memory Management**: Automatic worker restarts
- **Logging**: Comprehensive access and error logging

## 🔄 OCR Processing Flow

1. **Image Upload**: Client uploads image via `/api/upload_image`
2. **License Plate Detection**: YOLOv8 model detects plates in image
3. **Plate Cropping**: Best confidence plate is cropped with padding
4. **Character Recognition**: OCR model recognizes characters on cropped plate
5. **Text Assembly**: Characters sorted by position to form plate number
6. **Database Storage**: Results stored in history table
7. **Response**: Processed results returned to client

## 🛠️ Development

### Adding New Features

1. **Create Route Blueprint**
   ```python
   # app/routes/new_feature.py
   from flask import Blueprint
   
   new_feature_bp = Blueprint('new_feature', __name__)
   
   @new_feature_bp.route('/endpoint')
   def endpoint():
       return {'message': 'New feature'}
   ```

2. **Register Blueprint**
   ```python
   # app/__init__.py
   from .routes.new_feature import new_feature_bp
   app.register_blueprint(new_feature_bp, url_prefix='/feature')
   ```

3. **Add Business Logic**
   ```python
   # app/services/new_service.py
   def process_data(data):
       # Business logic here
       return processed_data
   ```

### Code Structure Guidelines

- **Routes**: Handle HTTP requests/responses only
- **Services**: Contain business logic
- **Utils**: Provide utility functions
- **Models**: Define data structures (future enhancement)

### Testing

```bash
# Run with debug mode
python wsgi.py

# Test endpoints
curl -X GET http://localhost:8000/health

# Test OCR upload
curl -X POST -F "image=@test_image.jpg" \
     "http://localhost:8000/api/upload_image?status=entering"
```

## 🚀 Deployment

### Production Deployment

1. **Server Setup**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python and dependencies
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

3. **Configure Services**
   ```bash
   # Create systemd service
   sudo nano /etc/systemd/system/carwatch.service
   ```

   ```ini
   [Unit]
   Description=CarWatch Backend
   After=network.target
   
   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/path/to/carwatch-backend
   Environment=PATH=/path/to/carwatch-backend/venv/bin
   ExecStart=/path/to/carwatch-backend/venv/bin/gunicorn --config gunicorn.conf.py wsgi:app
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Nginx Configuration**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:9036;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p logs uploads models

EXPOSE 8000

CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]
```

## 📊 Monitoring & Logging

### Log Files
- `logs/access.log`: HTTP access logs
- `logs/error.log`: Application errors
- `logs/app.log`: General application logs

### Log Rotation
Logs are automatically rotated when they reach 5MB, with 5 backup files retained.

### Monitoring Endpoints
- `GET /health`: Application health status
- `GET /`: Basic connectivity test

## 🔧 Troubleshooting

### Common Issues

1. **Model Files Missing**
   ```
   Error: Could not load YOLOv8 model
   Solution: Place model files in models/ directory
   ```

2. **Database Connection Failed**
   ```
   Error: Database connection error
   Solution: Check database credentials in .env file
   ```

3. **Memory Issues**
   ```
   Error: Out of memory during OCR processing
   Solution: Reduce image size or increase server memory
   ```

4. **Import Errors**
   ```
   Error: Module not found
   Solution: Ensure virtual environment is activated
   ```

### Performance Optimization

- Use single worker with threading for memory efficiency
- Implement image compression before OCR processing
- Add Redis caching for frequently accessed data
- Optimize database queries with proper indexing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -am 'Add new feature'`)
6. Push to the branch (`git push origin feature/new-feature`)
7. Create a Pull Request

### Development Guidelines

- Follow PEP 8 Python style guide
- Add docstrings to all functions
- Include error handling
- Write tests for new features
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Open an issue on GitHub
- **Documentation**: Check this README and code comments
- **Email**: Contact the maintainer for urgent issues

## 🔮 Future Enhancements

- [ ] Real-time WebSocket notifications
- [ ] Advanced analytics dashboard
- [ ] Multi-camera support
- [ ] Mobile app integration
- [ ] Cloud storage integration
- [ ] Advanced OCR post-processing
- [ ] API rate limiting
- [ ] Comprehensive test suite

---

**Version**: 1.0.0  
**Last Updated**: June 2024  
**Maintainer**: CarWatch Development Team
