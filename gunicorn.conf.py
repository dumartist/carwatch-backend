import multiprocessing
import os

# Server socket
bind = "0.0.0.0:9036"  # Listen on all interfaces, port 9036
backlog = 2048  # Maximum number of pending connections

# Worker processes - optimized for single-core VPS
cpu_count = multiprocessing.cpu_count()
if cpu_count == 1:
    workers = 1  # For single-core: 1-2 workers max
else:
    workers = multiprocessing.cpu_count() * 2 + 1

# Alternative: Single worker with threading
workers = 1
worker_class = "gthread"  # Use threading instead of processes
threads = 4  # 4 threads per worker
worker_connections = 1000
timeout = 120  # Higher timeout for ML processing

# Restart workers after this many requests (prevents memory leaks)
max_requests = 500  # Restart workers more frequently to prevent memory leaks
max_requests_jitter = 50

# Logging configuration
accesslog = "logs/access.log"  # Access log file path
errorlog = "logs/error.log"    # Error log file path
loglevel = "info"              # Logging level (debug, info, warning, error, critical)
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "carwatch-backend"

# Server mechanics
daemon = False  # Don't run as daemon (set to True for production)
pidfile = "logs/carwatch-backend.pid"  # Process ID file
user = None     # User to run as (Unix only)
group = None    # Group to run as (Unix only)

# Performance tuning for single-core
preload_app = True  # Important: reduces memory usage
worker_tmp_dir = "/tmp"  # Use system temp directory

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Print configuration info
print(f"Gunicorn workers: {workers} (CPU cores: {cpu_count})")
