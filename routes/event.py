from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2

from db import get_db_connection



event_bp = Blueprint('event', __name__)


@event_bp.route('/event_details/<int:event_id>')
def event_details(event_id):
    if session.get('user_role') != 'student':
        return redirect(url_for('auth.login'))  

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get the event
        cursor.execute("SELECT * FROM events WHERE event_id = %s", (event_id,))
        event = cursor.fetchone()

        if not event:
            flash('Event not found.')
            return redirect(url_for('student.student_dashboard'))

        # Just set is_registered to False for now
        is_registered = False  

    except Exception as e:
        print(f"Database error: {e}")
        flash('An error occurred loading event details.')
        return redirect(url_for('student.student_dashboard'))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    
    return render_template('event_details.html', event=event, is_registered=is_registered)


