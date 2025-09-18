import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

from db import get_db_connection




student_bp = Blueprint('student', __name__)



@student_bp.route('/student_dashboard')
def student_dashboard():
    if not session.get('user_role') == 'student':
        return redirect(url_for('login'))

    conn = None
    cursor = None

    user_department_id = session.get('user_department_id')
    user_id = session.get('user_id')

    events = []
    registered_events_list = []
    unread_notices = []
    read_notices = []

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Events
        cursor.execute("SELECT * FROM events ORDER BY event_date ASC")
        events = cursor.fetchall()

        # Registered events
        cursor.execute("SELECT event_id FROM registrations WHERE student_id = %s", (user_id,))
        registered_events_list = [row['event_id'] for row in cursor.fetchall()]

        # Notices (fake category)
        cursor.execute("""
            SELECT 
                notice_id, 
                title, 
                content, 
                sent_at,
                CASE 
                    WHEN recipient_id IS NULL THEN 'general'
                    ELSE 'event'
                END AS category
            FROM notices
            ORDER BY sent_at DESC
        """)
        notices_db = cursor.fetchall()

        for n in notices_db:
            mapped_notice = {
                'title': n['title'],
                'category': n['category'],
                'content': n['content'],
                'sent_at': n['sent_at']
            }
            unread_notices.append(mapped_notice)
            read_notices.append(mapped_notice)

        print("Fetched events:", len(events))
        print("Fetched notices:", len(notices_db))

    except Exception as e:
        print(f"Database error: {e}")
        flash('An error occurred loading the dashboard.')
        return render_template(
            'student_dashboard.html',
            error='An error occurred.',
            events=[],
            registered_events=[],
            unread_notices=[],
            read_notices=[],
            student_name=session.get('user_name')
        )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template(
        'student_dashboard.html',
        events=events,
        registered_events=registered_events_list,
        student_name=session.get('user_name'),
        unread_notices=unread_notices,
        read_notices=read_notices
    )










@student_bp.route('/register_event', methods=['POST'])
def register_event():
    if not session.get('user_role') == 'student':
        flash("You must be logged in to register for an event.")
        return redirect(url_for('login'))
    
    event_id = request.form.get('event_id')
    student_id = session.get('user_id')
    
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM registrations WHERE student_id = %s AND event_id = %s", (student_id, event_id))
        existing_registration = cursor.fetchone()
        
        if existing_registration:
            flash("You are already registered for this event.")
            return redirect(url_for('event_details', event_id=event_id))

        sql = "INSERT INTO registrations (student_id, event_id) VALUES (%s, %s)"
        cursor.execute(sql, (student_id, event_id))
        conn.commit()
        
        flash('Registration successful!')
        return redirect(url_for('confirm_registration', event_id=event_id))
        
    except mysql.Error as err:
     flash(f"Error: {err}")
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return redirect(url_for('student.student_dashboard'))



@student_bp.route('/confirm_registration/<int:event_id>')
def confirm_registration(event_id):
    if not session.get('user_role') == 'student':
        return redirect(url_for('login'))
        
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT event_name, event_date, description FROM events WHERE event_id = %s"
        cursor.execute(query, (event_id,))
        event = cursor.fetchone()
    
    except Exception as e:
        print(f"Database error: {e}")
        flash('An error occurred confirming registration.')
        return redirect(url_for('student.student_dashboard'))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    if event:
        return render_template('confirm_registration.html', event=event)
    return "Event not found", 404


def get_students_for_notice(recipient_id, target_year):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    students = []

    if recipient_id == 'all':
        cursor.execute('SELECT email FROM Students')
    else:
        # We need to filter by both department and year
        query = 'SELECT email FROM Students WHERE department_id = %s AND current_year = %s'
        cursor.execute(query, (recipient_id, target_year))

    students = cursor.fetchall()
    conn.close()
    return students