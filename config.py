import os
from dotenv import load_dotenv 

load_dotenv()

# --- MySQL Config ---
# Build the database URI dynamically from environment variables
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306") 
MYSQL_DB = os.getenv("MYSQL_DB")


# Secret key for sessions
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
