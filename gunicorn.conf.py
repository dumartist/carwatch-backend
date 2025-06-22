import multiprocessing
import os

bind = "127.0.0.1:9036"
bind = "0.0.0.0:9036"
backlog = 2048

cpu_count = multiprocessing.cpu_count()
if cpu_count == 1:
    workers = 1  # For single-core: 1-2 workers max
else:
    workers = multiprocessing.cpu_count() * 2 + 1

worker_class = "gthread"
threads = 2
worker_connections = 1000
timeout = 180

max_requests = 100
max_requests_jitter = 20
worker_tmp_dir = "/tmp"
preload_app = True

accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

proc_name = "carwatch-backend"
daemon = False
pidfile = "logs/carwatch-backend.pid"
user = None
group = None

os.makedirs('logs', exist_ok=True)
