import mysql.connector
import os
from dotenv import load_dotenv
import bcrypt

# Load environment variables
load_dotenv()

# Connect to MySQL
conn = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    database=os.getenv("MYSQL_DB"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    port=os.getenv("MYSQL_PORT")
)
cur = conn.cursor()

# ======================
# Create Tables
# ======================

cur.execute("""
CREATE TABLE IF NOT EXISTS departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'organizer'
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    year INT,
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    event_name VARCHAR(150) NOT NULL,
    description TEXT,
    event_date DATE,
    event_time TIME,
    location VARCHAR(150)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS registrations (
    reg_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    event_id INT,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS notices (
    notice_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    recipient_id INT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# ======================
# Insert Sample Data
# ======================

# Departments
cur.execute("""
INSERT INTO departments (name) VALUES
('BCA'), ('BBA')
ON DUPLICATE KEY UPDATE name = name;
""")

# Sample admin
password = "admin123"
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()
cur.execute("""
INSERT INTO admins (name, email, password, role) VALUES
(%s, %s, %s, %s)
ON DUPLICATE KEY UPDATE name=name;
""", ('Admin', 'admin@example.com', hashed_password, 'admin'))

# Sample student
student_password = "test123"
hashed_student_pw = bcrypt.hashpw(student_password.encode('utf-8'), bcrypt.gensalt()).decode()
cur.execute("""
INSERT INTO students (name, email, password, year, department_id) VALUES
(%s, %s, %s, %s, (SELECT department_id FROM departments WHERE name='BCA'))
ON DUPLICATE KEY UPDATE name=name;
""", ('Test Student', 'student@example.com', hashed_student_pw, 2))

# Sample events
cur.execute("""
INSERT INTO events (event_name, description, event_date, event_time, location) VALUES
('AI Workshop', 'Intro to AI', '2025-09-15', '10:00:00', 'Auditorium'),
('Hackathon', '24-hour coding competition', '2025-10-01', '09:00:00', 'Lab')
ON DUPLICATE KEY UPDATE event_name = event_name;
""")

# Commit and close
conn.commit()
cur.close()
conn.close()

print("Tables created and sample data inserted successfully!")
print("Test student login -> email: student@example.com | password: test123")