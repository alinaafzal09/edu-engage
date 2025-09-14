from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash


from db import get_db_connection



admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin_dashboard')
def admin_dashboard():
    # Check if the user is logged in and is an admin or organizer
    user_role = session.get('user_role')
    if user_role not in ('admin', 'organizer'):
        # Redirect to login with the correct endpoint
        return redirect(url_for('auth.login'))

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        #  Fetching Notices with Department Names
        query_notices = """
            SELECT n.title, n.content, n.sent_at,
                   CASE 
                       WHEN n.recipient_id IS NULL THEN 'All Students'
                       ELSE d.name
                   END AS recipient_name
            FROM notices n
            LEFT JOIN departments d ON n.recipient_id = d.department_id
            ORDER BY n.sent_at DESC
        """
        cursor.execute(query_notices)
        notices = cursor.fetchall()
        
        query_events = "SELECT * FROM events ORDER BY event_date DESC"
        cursor.execute(query_events)
        events = cursor.fetchall()

        query_registrations = """
            SELECT r.reg_id, s.name AS student_name, s.email, e.event_name
            FROM registrations r
            JOIN students s ON r.student_id = s.student_id
            JOIN events e ON r.event_id = e.event_id
            ORDER BY r.registered_at DESC
        """
        cursor.execute(query_registrations)
        registrations = cursor.fetchall()

    except Exception as e:
        print(f"Database error: {e}")
        flash('An error occurred loading the admin dashboard.')
        # Redirect to login with the correct endpoint on error
        return redirect(url_for('auth.login'))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('admin_dashboard.html', 
                           events=events, 
                           registrations=registrations, 
                           notices=notices,
                           admin_name=session.get('user_name'))


@admin_bp.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if not session.get('user_role') in ('admin', 'organizer'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        event_name = request.form['eventName']
        description = request.form['description']
        event_date = request.form['eventDate']
        
        conn = None
        cursor = None

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = "INSERT INTO events (event_name, description, event_date) VALUES (%s, %s, %s)"
            cursor.execute(sql, (event_name, description, event_date))
            conn.commit()
            flash('Event added successfully!')
            return redirect(url_for('manage_events'))
        except Exception as e:
            print(f"Database error: {e}")
            flash('An error occurred adding the event.')
            return redirect(url_for('add_event'))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        
    return render_template('add_event.html')

@admin_bp.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    if not session.get('user_role') in ('admin', 'organizer'):
        return redirect(url_for('login'))

    conn = None
    cursor = None
    event = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            event_name = request.form['eventName']
            description = request.form['description']
            event_date = request.form['eventDate']
            
            sql = "UPDATE events SET event_name = %s, description = %s, event_date = %s WHERE event_id = %s"
            cursor.execute(sql, (event_name, description, event_date, event_id))
            conn.commit()
            flash('Event updated successfully!')
            return redirect(url_for('manage_events'))
        
        query = "SELECT * FROM events WHERE event_id = %s"
        cursor.execute(query, (event_id,))
        event = cursor.fetchone()
    
    except Exception as e:
        print(f"Database error: {e}")
        flash('An error occurred editing the event.')
        return redirect(url_for('manage_events'))
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    if event:
        return render_template('edit_event.html', event=event)
    return "Event not found", 404

@admin_bp.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    if not session.get('user_role') in ('admin', 'organizer'):
        return redirect(url_for('login'))
        
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "DELETE FROM events WHERE event_id = %s"
        cursor.execute(sql, (event_id,))
        conn.commit()
        flash('Event deleted successfully!')
    except Exception as e:
        print(f"Database error: {e}")
        flash('An error occurred deleting the event.')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return redirect(url_for('manage_events'))



@admin_bp.route('/send_notice', methods=['GET', 'POST'])
def send_notice():
    # 1. Access Control
    if not session.get('user_role') in ('admin', 'organizer'):
        return redirect(url_for('login'))

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 2. Handle POST requests for different form actions
        if request.method == 'POST':
            # Handle Add/Delete Department
            if 'addDepartment' in request.form:
                new_department_name = request.form.get('newDepartmentName')
                if new_department_name:
                    sql = "INSERT INTO departments (name) VALUES (%s)"
                    cursor.execute(sql, (new_department_name,))
                    conn.commit()
                    flash('New department added successfully!')
                    return redirect(url_for('send_notice'))
            
            elif 'deleteDepartment' in request.form:
                department_id = request.form.get('departmentToDelete')
                if department_id:
                    sql = "DELETE FROM departments WHERE department_id = %s"
                    cursor.execute(sql, (department_id,))
                    conn.commit()
                    flash('Department deleted successfully!')
                    return redirect(url_for('send_notice'))
            
            # 3. Handle Send Notice action
            elif 'sendNotice' in request.form:
                title = request.form.get('noticeTitle')
                content = request.form.get('noticeContent')
                recipient_id = request.form.get('noticeRecipient')
                
                if not title or not content:
                    flash("Title and content are required.")
                    return redirect(url_for('send_notice'))

                # Check if the recipient is "all" and set recipient_id to None for the database
                if recipient_id == 'all':
                    recipient_id = None
                
                sql = "INSERT INTO notices (title, content, recipient_id) VALUES (%s, %s, %s)"
                cursor.execute(sql, (title, content, recipient_id))
                conn.commit()
                
                flash('Notice sent successfully!')
                return redirect(url_for('send_notice'))
        
        # 4. Fetch data for the page (GET or POST)
        cursor.execute("SELECT department_id, name FROM departments ORDER BY name")
        departments = cursor.fetchall()
        
        # --- INSERTED query_notices block ---
        query_notices = """
            SELECT 
                n.notice_id, 
                n.title, 
                n.content, 
                n.sent_at,
                CASE 
                    WHEN n.recipient_id IS NULL THEN 'All Students'
                    ELSE d.name
                END AS recipient_name
            FROM notices n
            LEFT JOIN departments d ON n.recipient_id = d.department_id
            ORDER BY n.sent_at DESC
        """
        cursor.execute(query_notices)
        notices = cursor.fetchall()
    
    except Exception as e:
        print(f"Database error: {e}")
        flash('An error occurred.')
        notices = []
        departments = []
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return render_template('send_notice.html', notices=notices, departments=departments)



@admin_bp.route('/reports')
def reports():
    if not session.get('user_role') in ('admin', 'organizer'):
        return redirect(url_for('login'))
        
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query_registrations = """
            SELECT e.event_name, COUNT(r.reg_id) AS total_registrations
            FROM registrations r
            JOIN students s ON r.student_id = s.student_id
            JOIN events e ON r.event_id = e.event_id
            GROUP BY e.event_name
            ORDER BY total_registrations DESC
        """
        cursor.execute(query_registrations)
        registration_summary = cursor.fetchall()
    except Exception as e:
        print(f"Database error: {e}")
        flash('An error occurred generating the report.')
        return redirect(url_for('admin_dashboard'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return render_template('reports.html', registration_summary=registration_summary)

@admin_bp.route('/delete_notice/<int:notice_id>', methods=['GET'])
def delete_notice(notice_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Delete the notice
    cursor.execute("DELETE FROM notices WHERE id = %s", (notice_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash("Notice deleted successfully", "success")
    return redirect(url_for('admin.send_notice'))

@admin_bp.route('/manage_events', methods=['GET', 'POST'])
def manage_events():
    if not session.get('user_role') in ('admin', 'organizer'):
        return redirect(url_for('login'))

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query_events = "SELECT * FROM events ORDER BY event_date DESC"
        cursor.execute(query_events)
        events = cursor.fetchall()

    except Exception as e:
        print(f"Database error: {e}")
        flash('An error occurred loading events.')
        events = []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('manage_events.html', events=events)
