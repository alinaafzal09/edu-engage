import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

def get_db_connection():
    """
    Establishes a connection to the MySQL database using environment variables.
    """
    try:
        conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DB"),
            port=os.getenv("MYSQL_PORT", "3306")
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

# for testing):
if __name__ == '__main__':
    conn = get_db_connection()
    if conn and conn.is_connected():
        print("Successfully connected to MySQL database!")
        conn.close()
    else:
        print("Failed to connect to MySQL database.")
