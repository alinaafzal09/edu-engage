from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from db import get_db_connection



auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = None
        cursor = None
        user = None

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            #  Check if admin
            query_admin = """
                SELECT admin_id AS id, password, role, name
                FROM admins
                WHERE email = %s
            """
            cursor.execute(query_admin, (email,))
            user = cursor.fetchone()

            #  If not admin, check if student
            if not user:
                query_student = """
                    SELECT student_id AS id, password, 'student' AS role, name, department_id
                    FROM students
                    WHERE email = %s
                """
                cursor.execute(query_student, (email,))
                user = cursor.fetchone()

        except Exception as e:
            print(f"Database error: {e}")
            flash('An error occurred. Please try again later.')
            return render_template('login.html', error='An error occurred.')

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        #  Verify password and set session
        if user and check_password_hash(user['password'], password):
            session['logged_in'] = True
            session['user_id'] = user['id']
            session['user_role'] = user['role']
            session['user_name'] = user['name']

            # Set department for student only
            if user['role'] == 'student' and 'department_id' in user:
                session['user_department_id'] = user['department_id']

            # Redirect based on role
            if user['role'] == 'student':
                return redirect(url_for('student.student_dashboard'))
            else:
                return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Invalid email or password.')
            return render_template('login.html', error='Invalid email or password.')

    # GET request
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('user_role', None)
    session.pop('user_name', None)
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    conn = None
    cursor = None
    departments = []

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT department_id, name FROM departments")
        departments = cursor.fetchall()

        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            year = request.form['year']
            department_id = request.form['department']

            cursor.execute("SELECT student_id FROM students WHERE email = %s", (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash('Email already registered. Please login.')
                return redirect(url_for('auth.login'))

            hashed_password = generate_password_hash(password)
            sql = "INSERT INTO students (name, email, password, year, department_id) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (name, email, hashed_password, year, department_id))
            conn.commit()

            flash('Registration successful! Please login.')
            return redirect(url_for('auth.login'))

    except Exception as e:
        print(f"Database error: {e}")
        flash('An error occurred. Please try again later.')
        return render_template('register.html', departments=departments)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('register.html', departments=departments)






