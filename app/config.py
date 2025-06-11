import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Database configuration
    DB_HOST = os.getenv("DB_HOST", "database.xetf.my.id")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "Ehetenandayo123")
    DB_NAME = os.getenv("DB_NAME", "carwatch")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "fa9ad7597c3d00bfee0003ab96cd6cd70448e1202193bb9dcce7308fda931100")
    BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))
    
    # Application settings
    DEBUG = False