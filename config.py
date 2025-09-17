import os
from dotenv import load_dotenv 


load_dotenv()

# --- PostgreSQL Config ---
# It's build the database URI dynamically from environment variables
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")        
POSTGRES_DB = os.getenv("POSTGRES_DB")


# Secret key for sessions
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
