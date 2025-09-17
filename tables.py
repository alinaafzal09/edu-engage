import psycopg2
from psycopg2 import sql
import bcrypt
import config

# Connect to Postgres
conn = psycopg2.connect(
    host=config.POSTGRES_HOST,
    database=config.POSTGRES_DB,
    user=config.POSTGRES_USER,
    password=config.POSTGRES_PASSWORD,
    port=config.POSTGRES_PORT
)
cur = conn.cursor()

# ======================
# Create Tables
# ======================

cur.execute("""
CREATE TABLE IF NOT EXISTS departments (
    department_id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS admins (
    admin_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'organizer'
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    year INT,
    department_id INT REFERENCES departments(department_id)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS events (
    event_id SERIAL PRIMARY KEY,
    event_name VARCHAR(150) NOT NULL,
    description TEXT,
    event_date DATE,
    event_time TIME,
    location VARCHAR(150)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS registrations (
    reg_id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(student_id),
    event_id INT REFERENCES events(event_id),
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS notices (
    notice_id SERIAL PRIMARY KEY,
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
ON CONFLICT (name) DO NOTHING;
""")

# Sample admin
password = "admin123"
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()
cur.execute("""
INSERT INTO admins (name, email, password, role) VALUES
(%s, %s, %s, %s)
ON CONFLICT (email) DO NOTHING;
""", ('Admin', 'admin@example.com', hashed_password, 'admin'))

# Sample student
student_password = "test123"
hashed_student_pw = bcrypt.hashpw(student_password.encode('utf-8'), bcrypt.gensalt()).decode()
cur.execute("""
INSERT INTO students (name, email, password, year, department_id) VALUES
(%s, %s, %s, %s, (SELECT department_id FROM departments WHERE name='BCA'))
ON CONFLICT (email) DO NOTHING;
""", ('Test Student', 'student@example.com', hashed_student_pw, 2))

# Sample events
cur.execute("""
INSERT INTO events (event_name, description, event_date, event_time, location) VALUES
('AI Workshop', 'Intro to AI', '2025-09-15', '10:00:00', 'Auditorium'),
('Hackathon', '24-hour coding competition', '2025-10-01', '09:00:00', 'Lab')
ON CONFLICT DO NOTHING;
""")

# Commit and close
conn.commit()
cur.close()
conn.close()

print("Tables created and sample data inserted successfully!")
print("Test student login -> email: student@example.com | password: test123")



