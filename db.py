import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()

def get_db_connection():
    """Return a psycopg2 connection to Postgres using env vars."""
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD", ""),
        database=os.getenv("POSTGRES_DB")
    )
    return conn

