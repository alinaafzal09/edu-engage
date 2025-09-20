import os
from dotenv import load_dotenv

load_dotenv()
import mysql.connector
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import config
from datetime import datetime
from routes.event import event_bp


app = Flask(__name__)


app.secret_key = os.getenv('SECRET_KEY')



def get_db_connection():
    """Connect to MySQL database using environment variables."""
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        database=os.getenv("MYSQL_DB"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        port=int(os.getenv("MYSQL_PORT", 3306))
    )


# routes
@app.route('/')
def landing():
    return render_template('landing.html')




@app.route('/test')
def test():
    return "Flask is working"

# Import and register blueprints 
from routes.auth import auth_bp
from routes.student import student_bp
from routes.admin import admin_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(event_bp, url_prefix='/event')




 
# For debugging purposes, can uncomment this to see all registered routes
# for rule in app.url_map.iter_rules():
#     print(rule)


if __name__ == "__main__":
    app.run(debug=True)

