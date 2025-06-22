FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for OpenCV and other packages
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libpng-dev \
    libjpeg-dev \
    python3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create required directories
RUN mkdir -p logs uploads models

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip/*

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose the port the app runs on
EXPOSE 9036

# Command to run the application using gunicorn
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]
