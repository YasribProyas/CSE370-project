from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app.proyas import proyas_bp
from app.db import execute_query
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id') or not session.get('is_admin'):
            flash('You need admin access to view this page', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function



@proyas_bp.route('/admin')
@admin_required
def admin_dashboard():
    animals_count = execute_query("SELECT COUNT(*) as count FROM Animal", fetch=True)
    users_count = execute_query("SELECT COUNT(*) as count FROM User", fetch=True)
    admins_count = execute_query("SELECT COUNT(*) as count FROM Admin", fetch=True)
    consultants_count = execute_query("SELECT COUNT(*) as count FROM Consultant", fetch=True)
    
    animals = execute_query("SELECT * FROM Animal LIMIT 10", fetch=True)
    admins = execute_query("""SELECT u.id, u.name, u.email FROM User u 
                             INNER JOIN Admin a ON u.id = a.user_id LIMIT 10""", fetch=True)
    consultants = execute_query("""SELECT u.id, u.name, u.email, c.full_name, c.phone_no, c.address 
                                  FROM User u 
                                  INNER JOIN Consultant c ON u.id = c.user_id LIMIT 10""", fetch=True)
    general_users = execute_query("""SELECT u.id, u.name, u.email FROM User u 
                                    WHERE u.id NOT IN (SELECT user_id FROM Admin) 
                                    AND u.id NOT IN (SELECT user_id FROM Consultant) LIMIT 10""", fetch=True)
    
    # Get pending consultations
    consultations_query = """
        SELECT a.*, 
               u.name as user_name, 
               c.full_name as consultant_full_name,
               uc.name as consultant_name
        FROM Appointment a
        INNER JOIN Adopter ad ON a.adopter_id = ad.user_id
        INNER JOIN User u ON a.adopter_id = u.id
        INNER JOIN Consultant c ON a.consultant_id = c.user_id
        INNER JOIN User uc ON a.consultant_id = uc.id
        WHERE a.animal_id IS NULL
        ORDER BY a.date ASC, a.timeslot_id ASC
        LIMIT 10
    """
    pending_consultations = execute_query(consultations_query, fetch=True) or []
    
    # Add time slot information
    for consultation in pending_consultations:
        consultation['slot_time'] = get_slot_time(consultation['timeslot_id'])
    
    # Get pending adoption requests (not yet scheduled)
    adoptions_query = """
        SELECT a.*, an.title, an.breed, an.type, u.name as adopter_name, ad.full_name, ad.phone_no
        FROM Adopt a
        INNER JOIN Animal an ON a.animal_id = an.id
        INNER JOIN Adopter ad ON a.adopter_id = ad.user_id
        INNER JOIN User u ON a.adopter_id = u.id
        WHERE a.approved = FALSE
        ORDER BY a.adoption_date DESC
        LIMIT 10
    """
    pending_adoptions = execute_query(adoptions_query, fetch=True) or []
    
    return render_template('/admin_dashboard.html',
                         animals_count=animals_count[0]['count'] if animals_count else 0,
                         users_count=users_count[0]['count'] if users_count else 0,
                         admins_count=admins_count[0]['count'] if admins_count else 0,
                         consultants_count=consultants_count[0]['count'] if consultants_count else 0,
                         animals=animals or [],
                         admins=admins or [],
                         consultants=consultants or [],
                         general_users=general_users or [],
                         pending_consultations=pending_consultations,
                         pending_adoptions=pending_adoptions)


@proyas_bp.route('/admin/animals')
@admin_required
def manage_animals():
    animals = execute_query("SELECT * FROM Animal", fetch=True)
    return render_template('/manage_animals.html', animals=animals or [])

@proyas_bp.route('/admin/animals/add', methods=['GET', 'POST'])
@admin_required
def add_animal():
    if request.method == 'POST':
        title = request.form.get('title')
        animal_type = request.form.get('type')
        breed = request.form.get('breed')
        color = request.form.get('color')
        age = request.form.get('age')
        sex = request.form.get('sex')
        size = request.form.get('size')
        weight = request.form.get('weight')
        training = request.form.get('training')
        description = request.form.get('description')
        diet = request.form.get('diet')
        behaviour = request.form.get('behaviour')
        img_url = request.form.get('img_url')
        
        if not all([title, animal_type, breed, color, age]):
            flash('Please fill all required fields', 'danger')
            return render_template('/add_animal.html')
        
        id_query = "SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM Animal"
        result = execute_query(id_query, fetch=True)
        next_id = result[0]['next_id'] if result else 1
        
        insert_query = """INSERT INTO Animal (id, title, type, breed, color, age, sex, size, weight, 
                          training, description, diet, behaviour, img_url) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        execute_query(insert_query, (next_id, title, animal_type, breed, color, age, sex, size, 
                                     weight, training, description, diet, behaviour, img_url))
        
        flash('Animal added successfully!', 'success')
        return redirect(url_for('proyas.manage_animals'))
    
    return render_template('/add_animal.html')

@proyas_bp.route('/admin/animals/edit/<int:animal_id>', methods=['GET', 'POST'])
@admin_required
def edit_animal(animal_id):
    animal = execute_query("SELECT * FROM Animal WHERE id = %s", (animal_id,), fetch=True)
    
    if not animal:
        flash('Animal not found', 'danger')
        return redirect(url_for('proyas.manage_animals'))
    
    animal = animal[0]
    
    if request.method == 'POST':
        title = request.form.get('title')
        animal_type = request.form.get('type')
        breed = request.form.get('breed')
        color = request.form.get('color')
        age = request.form.get('age')
        sex = request.form.get('sex')
        size = request.form.get('size')
        weight = request.form.get('weight')
        training = request.form.get('training')
        description = request.form.get('description')
        diet = request.form.get('diet')
        behaviour = request.form.get('behaviour')
        img_url = request.form.get('img_url')
        
        if not all([title, animal_type, breed, color, age]):
            flash('Please fill all required fields', 'danger')
            return render_template('/edit_animal.html', animal=animal)
        
        update_query = """UPDATE Animal SET title=%s, type=%s, breed=%s, color=%s, age=%s, 
                          sex=%s, size=%s, weight=%s, training=%s, description=%s, 
                          diet=%s, behaviour=%s, img_url=%s WHERE id=%s"""
        
        execute_query(update_query, (title, animal_type, breed, color, age, sex, size, weight,
                                     training, description, diet, behaviour, img_url, animal_id))
        
        flash('Animal updated successfully!', 'success')
        return redirect(url_for('proyas.manage_animals'))
    
    return render_template('/edit_animal.html', animal=animal)

@proyas_bp.route('/admin/animals/delete/<int:animal_id>', methods=['POST'])
@admin_required
def delete_animal(animal_id):
    animal = execute_query("SELECT * FROM Animal WHERE id = %s", (animal_id,), fetch=True)
    
    if not animal:
        flash('Animal not found', 'danger')
        return redirect(url_for('proyas.manage_animals'))
    
    execute_query("DELETE FROM Animal WHERE id = %s", (animal_id,))
    flash('Animal deleted successfully!', 'success')
    return redirect(url_for('proyas.manage_animals'))



@proyas_bp.route('/admin/users')
@admin_required
def manage_users():
    users = execute_query("""SELECT u.*, 
                           CASE 
                               WHEN a.user_id IS NOT NULL THEN 'Admin'
                               WHEN c.user_id IS NOT NULL THEN 'Consultant'
                               ELSE 'General User'
                           END as role
                           FROM User u
                           LEFT JOIN Admin a ON u.id = a.user_id
                           LEFT JOIN Consultant c ON u.id = c.user_id""", fetch=True)
    return render_template('/manage_users.html', users=users or [])

@proyas_bp.route('/admin/users/make-admin/<int:user_id>', methods=['POST'])
@admin_required
def make_admin(user_id):
    user = execute_query("SELECT * FROM User WHERE id = %s", (user_id,), fetch=True)
    
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('proyas.manage_users'))
    
    existing = execute_query("SELECT * FROM Admin WHERE user_id = %s", (user_id,), fetch=True)
    
    if existing:
        flash('User is already an admin', 'warning')
        return redirect(url_for('proyas.manage_users'))
    
    execute_query("INSERT INTO Admin (user_id) VALUES (%s)", (user_id,))
    flash(f'User {user[0]["name"]} is now an admin!', 'success')
    return redirect(url_for('proyas.manage_users'))


@proyas_bp.route('/admin/users/add-consultant', methods=['GET', 'POST'])
@admin_required
def add_consultant():
    users = execute_query("""SELECT u.* FROM User u 
                           WHERE u.id NOT IN (SELECT user_id FROM Consultant)
                           AND u.id NOT IN (SELECT user_id FROM Admin)""", fetch=True)
    
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        full_name = request.form.get('full_name')
        phone_no = request.form.get('phone_no')
        address = request.form.get('address')
        
        if not all([user_id, full_name, phone_no, address]):
            flash('Please fill all required fields', 'danger')
            return render_template('/add_consultant.html', users=users or [])
        
        existing = execute_query("SELECT * FROM Consultant WHERE user_id = %s", (user_id,), fetch=True)
        
        if existing:
            flash('User is already a consultant', 'warning')
            return render_template('/add_consultant.html', users=users or [])
        
        insert_query = """INSERT INTO Consultant (user_id, full_name, phone_no, address) 
                         VALUES (%s, %s, %s, %s)"""
        execute_query(insert_query, (user_id, full_name, phone_no, address))
        
        flash('Consultant added successfully!', 'success')
        return redirect(url_for('proyas.manage_users'))
    
    return render_template('/add_consultant.html', users=users or [])


@proyas_bp.route('/admin/users/remove-admin/<int:user_id>', methods=['POST'])
@admin_required
def remove_admin(user_id):
    admin = execute_query("SELECT * FROM Admin WHERE user_id = %s", (user_id,), fetch=True)
    
    if not admin:
        flash('Admin not found', 'danger')
        return redirect(url_for('proyas.manage_users'))
    
    execute_query("DELETE FROM Admin WHERE user_id = %s", (user_id,))
    flash('Admin access removed!', 'success')
    return redirect(url_for('proyas.manage_users'))



@proyas_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if not session.get('user_id'):
        flash('You need to be logged in to view your profile', 'danger')
        return redirect(url_for('auth.login'))
    
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        user = execute_query("SELECT * FROM User WHERE id = %s", (user_id,), fetch=True)
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('main.index'))
        
        user = user[0]
        
        if not name or not email:
            flash('Name and email are required', 'danger')
            return render_template('profile.html', user=user)
        
        if email != user['email']:
            existing = execute_query("SELECT * FROM User WHERE email = %s AND id != %s", (email, user_id), fetch=True)
            if existing:
                flash('Email is already in use', 'danger')
                return render_template('profile.html', user=user)
        
        if new_password or confirm_password:
            if not current_password:
                flash('Current password is required to change password', 'danger')
                return render_template('profile.html', user=user)
            
            if not check_password_hash(user['pass'], current_password):
                flash('Current password is incorrect', 'danger')
                return render_template('profile.html', user=user)
            
            if new_password != confirm_password:
                flash('New passwords do not match', 'danger')
                return render_template('profile.html', user=user)
            
            if len(new_password) < 6:
                flash('Password must be at least 6 characters', 'danger')
                return render_template('profile.html', user=user)
            
            hashed_password = generate_password_hash(new_password)
            update_query = "UPDATE User SET name=%s, email=%s, pass=%s WHERE id=%s"
            execute_query(update_query, (name, email, hashed_password, user_id))
        else:
            update_query = "UPDATE User SET name=%s, email=%s WHERE id=%s"
            execute_query(update_query, (name, email, user_id))
        
        session['user_name'] = name
        session['user_email'] = email
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('proyas.profile'))
    
    user = execute_query("SELECT * FROM User WHERE id = %s", (user_id,), fetch=True)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('profile.html', user=user[0])


@proyas_bp.route('/notifications')
def get_notifications():
    if not session.get('user_id'):
        return jsonify({'notifications': [], 'error': 'Not logged in'}), 401
    
    user_id = session.get('user_id')
    notifications = execute_query(
        "SELECT id, title, content FROM Notification WHERE user_id = %s ORDER BY id DESC",
        (user_id,),
        fetch=True
    ) or []
    
    return jsonify({'notifications': notifications})


@proyas_bp.route('/notifications/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    if not session.get('user_id'):
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session.get('user_id')
    
    # Verify notification belongs to the user
    notification = execute_query(
        "SELECT * FROM Notification WHERE id = %s AND user_id = %s",
        (notification_id, user_id),
        fetch=True
    )
    
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    execute_query("DELETE FROM Notification WHERE id = %s", (notification_id,))
    return jsonify({'success': True})


# ============== CONSULTATION ROUTES ==============
def get_slot_time(slot_number):
    """Convert slot number (1-6) to time range"""
    # Handle None or empty string
    if not slot_number or slot_number == '':
        return "N/A"
    
    try:
        slot_number = int(slot_number)
    except (ValueError, TypeError):
        return "N/A"
    
    start_hour = 10 + (slot_number - 1)
    end_hour = start_hour
    end_minute = 50
    
    start_time = f"{start_hour:02d}:00"
    end_time = f"{end_hour:02d}:{end_minute:02d}"
    return f"{start_time} - {end_time}"


@proyas_bp.route('/consultants')
def consultants():
    """View all consultants"""
    query = """
        SELECT u.id, u.name, c.full_name, c.phone_no, c.address
        FROM User u
        INNER JOIN Consultant c ON u.id = c.user_id
        ORDER BY u.name
    """
    consultants = execute_query(query, fetch=True) or []
    return render_template('consultants.html', consultants=consultants)


@proyas_bp.route('/book-consultation/<int:consultant_id>', methods=['GET', 'POST'])
def book_consultation(consultant_id):
    """Book a consultation"""
    if 'user_id' not in session:
        flash('Please login to book a consultation', 'warning')
        return redirect(url_for('auth.login'))
    
    # Get consultant details
    consultant_query = """
        SELECT u.id, u.name, c.full_name, c.phone_no, c.address
        FROM User u
        INNER JOIN Consultant c ON u.id = c.user_id
        WHERE u.id = %s
    """
    consultant = execute_query(consultant_query, (consultant_id,), fetch=True)
    
    if not consultant:
        flash('Consultant not found', 'danger')
        return redirect(url_for('proyas.consultants'))
    
    consultant = consultant[0]
    
    # Check if user is an adopter
    check_adopter = "SELECT * FROM Adopter WHERE user_id = %s"
    adopter = execute_query(check_adopter, (session['user_id'],), fetch=True)
    
    if not adopter:
        flash('Please complete your adopter profile before booking a consultation', 'info')
        return redirect(url_for('main.index'))
    
    # Get available time slots for next 7 days
    available_slots = {}
    today = datetime.now().date()
    
    for i in range(7):
        date = today + timedelta(days=i)
        # Get booked slots for this date and consultant
        booked_query = """
            SELECT timeslot_id FROM Appointment 
            WHERE consultant_id = %s AND date = %s
        """
        booked = execute_query(booked_query, (consultant_id, date), fetch=True) or []
        booked_slot_ids = [str(b['timeslot_id']) for b in booked]
        
        # Create slots 1-6
        slots = []
        for slot_num in range(1, 7):
            slot_id = slot_num
            is_booked = str(slot_id) in booked_slot_ids
            slots.append({
                'id': slot_id,
                'number': slot_num,
                'time': get_slot_time(slot_num),
                'booked': is_booked
            })
        
        available_slots[date.isoformat()] = {
            'date': date.strftime('%A, %B %d, %Y'),
            'slots': slots
        }
    
    if request.method == 'POST':
        selected_date = request.form.get('date')
        selected_slot = request.form.get('slot')
        amount = request.form.get('amount')
        method = request.form.get('method')
        trx_id = request.form.get('trx_id')
        
        # Validate inputs
        if not all([selected_date, selected_slot, method]):
            flash('All fields are required', 'danger')
            return render_template('book_consultation.html', 
                                 consultant=consultant, 
                                 available_slots=available_slots,
                                 adopter=adopter[0])
        
        if method != 'Cash on Delivery' and not trx_id:
            flash('Transaction ID is required for online payments', 'danger')
            return render_template('book_consultation.html', 
                                 consultant=consultant, 
                                 available_slots=available_slots,
                                 adopter=adopter[0])
        
        # Check if slot is still available
        check_slot = "SELECT * FROM Appointment WHERE consultant_id = %s AND date = %s AND timeslot_id = %s"
        existing = execute_query(check_slot, (consultant_id, selected_date, selected_slot), fetch=True)
        
        if existing:
            flash('This time slot is no longer available', 'danger')
            return render_template('book_consultation.html', 
                                 consultant=consultant, 
                                 available_slots=available_slots,
                                 adopter=adopter[0])
        
        # Get next appointment ID or use a combination key
        # Since we're using composite primary key, we just insert
        insert_query = """
            INSERT INTO Appointment (adopter_id, consultant_id, timeslot_id, date, trx_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        result = execute_query(insert_query, (session['user_id'], consultant_id, selected_slot, selected_date, trx_id or ''))
        
        if result is not None:
            flash('Consultation booked successfully! Awaiting admin confirmation.', 'success')
            return redirect(url_for('proyas.my_consultations'))
        else:
            flash('Failed to book consultation', 'danger')
    
    return render_template('book_consultation.html', 
                         consultant=consultant, 
                         available_slots=available_slots,
                         adopter=adopter[0])


@proyas_bp.route('/my-consultations')
def my_consultations():
    """View user's consultation bookings"""
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('auth.login'))
    
    # If user is a consultant, show both consultations and adoption appointments
    is_consultant_query = "SELECT user_id FROM Consultant WHERE user_id = %s"
    is_consultant = execute_query(is_consultant_query, (session['user_id'],), fetch=True)
    
    consultations = []
    adoptions = []
    
    if is_consultant:
        # Get consultation bookings where user is the consultant (animal_id IS NULL)
        consult_query = """
            SELECT a.*, u.name as adopter_name, 'consultation' as type
            FROM Appointment a
            INNER JOIN User u ON a.adopter_id = u.id
            WHERE a.consultant_id = %s AND a.animal_id IS NULL
            ORDER BY a.date DESC, a.timeslot_id
        """
        consultations = execute_query(consult_query, (session['user_id'],), fetch=True) or []
        
        # Get adoption appointments where user is the consultant (animal_id IS NOT NULL)
        adopt_query = """
            SELECT ap.*, an.title as animal_name, u.name as adopter_name, 'adoption' as type
            FROM Appointment ap
            INNER JOIN User u ON ap.adopter_id = u.id
            INNER JOIN Animal an ON ap.animal_id = an.id
            INNER JOIN Adopt ad ON ad.animal_id = ap.animal_id AND ad.adopter_id = ap.adopter_id
            WHERE ap.consultant_id = %s
            AND ap.animal_id IS NOT NULL
            AND ad.approved = FALSE
            ORDER BY ap.date DESC, ap.timeslot_id
        """
        adoptions = execute_query(adopt_query, (session['user_id'],), fetch=True) or []
        
        # Add time slot information to both
        for item in consultations:
            item['slot_time'] = get_slot_time(item['timeslot_id'])
        for item in adoptions:
            item['slot_time'] = get_slot_time(item['timeslot_id'])
    else:
        # Regular adopter viewing their consultations (animal_id IS NULL)
        query = """
            SELECT a.*, u.name as consultant_name, c.full_name as consultant_full_name, 'consultation' as type
            FROM Appointment a
            INNER JOIN User u ON a.consultant_id = u.id
            INNER JOIN Consultant c ON a.consultant_id = c.user_id
            WHERE a.adopter_id = %s AND a.animal_id IS NULL
            ORDER BY a.date DESC, a.timeslot_id
        """
        consultations = execute_query(query, (session['user_id'],), fetch=True) or []
        
        # Add time slot information
        for consultation in consultations:
            consultation['slot_time'] = get_slot_time(consultation['timeslot_id'])
    
    return render_template('my_consultations.html', consultations=consultations, adoptions=adoptions, is_consultant=bool(is_consultant))


@proyas_bp.route('/cancel-consultation/<int:consultant_id>/<consultation_date>/<int:slot_id>', methods=['POST'])
def cancel_consultation(consultant_id, consultation_date, slot_id):
    """Cancel a consultation booking"""
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('auth.login'))
    
    # Check if consultation exists and belongs to user
    check_query = """
        SELECT * FROM Appointment 
        WHERE adopter_id = %s AND consultant_id = %s AND date = %s AND timeslot_id = %s
    """
    consultation = execute_query(check_query, (session['user_id'], consultant_id, consultation_date, slot_id), fetch=True)
    
    if not consultation:
        flash('Consultation not found', 'danger')
        return redirect(url_for('proyas.my_consultations'))
    
    # Check if link is already set
    if consultation[0]['link'] and consultation[0]['link'] != '0':
        flash('Cannot cancel a consultation that has been confirmed with a meeting link', 'danger')
        return redirect(url_for('proyas.my_consultations'))
    
    # Delete consultation
    delete_query = """
        DELETE FROM Appointment 
        WHERE adopter_id = %s AND consultant_id = %s AND date = %s AND timeslot_id = %s
    """
    result = execute_query(delete_query, (session['user_id'], consultant_id, consultation_date, slot_id))
    
    if result is not None:
        flash('Consultation cancelled successfully', 'info')
    else:
        flash('Failed to cancel consultation', 'danger')
    
    return redirect(url_for('proyas.my_consultations'))


@proyas_bp.route('/admin/consultations')
@admin_required
def admin_consultations():
    """Admin view all pending consultations (exclude adoptions)"""
    query = """
        SELECT a.*, 
               u.name as user_name, 
               c.full_name as consultant_full_name,
               uc.name as consultant_name
        FROM Appointment a
        INNER JOIN Adopter ad ON a.adopter_id = ad.user_id
        INNER JOIN User u ON a.adopter_id = u.id
        INNER JOIN Consultant c ON a.consultant_id = c.user_id
        INNER JOIN User uc ON a.consultant_id = uc.id
        WHERE a.animal_id IS NULL
        ORDER BY a.date ASC, a.timeslot_id ASC
    """
    consultations = execute_query(query, fetch=True) or []
    
    # Add time slot information
    for consultation in consultations:
        consultation['slot_time'] = get_slot_time(consultation['timeslot_id'])
    
    return render_template('admin_consultations.html', consultations=consultations)


@proyas_bp.route('/admin/consultations/set-link/<int:adopter_id>/<int:consultant_id>/<consultation_date>/<int:slot_id>', methods=['POST'])
@admin_required
def set_consultation_link(adopter_id, consultant_id, consultation_date, slot_id):
    """Admin sets meeting link for consultation"""
    link = request.form.get('link')
    
    if not link:
        flash('Meeting link is required', 'danger')
        return redirect(url_for('proyas.admin_consultations'))
    
    # Update appointment with link
    update_query = """
        UPDATE Appointment 
        SET link = %s 
        WHERE adopter_id = %s AND consultant_id = %s AND date = %s AND timeslot_id = %s
    """
    result = execute_query(update_query, (link, adopter_id, consultant_id, consultation_date, slot_id))
    
    if result is not None:
        # Get user and consultant details for notification
        user_query = "SELECT id, name, email FROM User WHERE id = %s"
        user = execute_query(user_query, (adopter_id,), fetch=True)[0]
        
        consultant_query = "SELECT id, name FROM User WHERE id = %s"
        consultant = execute_query(consultant_query, (consultant_id,), fetch=True)[0]
        
        slot_time = get_slot_time(slot_id)
        notification_date = datetime.strptime(consultation_date, '%Y-%m-%d')
        formatted_date = notification_date.strftime('%B %d, %Y')
        
        # Create notification for user
        user_notif_title = "Consultation Confirmed!"
        user_notif_content = f"Your consultation with {consultant['name']} has been scheduled. Date: {formatted_date}, Time: {slot_time}. Meeting Link: {link}"
        
        user_notif_id_query = "SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM Notification"
        user_notif_id = execute_query(user_notif_id_query, fetch=True)[0]['next_id']
        
        user_insert = "INSERT INTO Notification (id, title, content, user_id) VALUES (%s, %s, %s, %s)"
        execute_query(user_insert, (user_notif_id, user_notif_title, user_notif_content, adopter_id))
        
        # Create notification for consultant
        consultant_notif_title = "New Consultation Scheduled!"
        consultant_notif_content = f"Consultation confirmed with {user['name']}. Date: {formatted_date}, Time: {slot_time}. Meeting Link: {link}"
        
        consultant_notif_id_query = "SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM Notification"
        consultant_notif_id = execute_query(consultant_notif_id_query, fetch=True)[0]['next_id']
        
        consultant_insert = "INSERT INTO Notification (id, title, content, user_id) VALUES (%s, %s, %s, %s)"
        execute_query(consultant_insert, (consultant_notif_id, consultant_notif_title, consultant_notif_content, consultant_id))
        
        flash('Meeting link set and notifications sent!', 'success')
    else:
        flash('Failed to set meeting link', 'danger')
    
    return redirect(url_for('proyas.admin_consultations'))


# ============== ADOPTION APPROVAL ROUTES ==============
@proyas_bp.route('/adoptions/approve/<int:adopter_id>/<int:consultant_id>/<adoption_date>/<int:slot_id>', methods=['POST'])
def approve_adoption(adopter_id, consultant_id, adoption_date, slot_id):
    """Consultant approves an adoption appointment"""
    if 'user_id' not in session or session['user_id'] != consultant_id:
        flash('You do not have permission to approve this adoption', 'danger')
        return redirect(url_for('proyas.my_consultations'))
    
    # Get the animal_id from the appointment
    appointment_query = """
        SELECT animal_id FROM Appointment
        WHERE adopter_id = %s AND consultant_id = %s AND date = %s AND timeslot_id = %s AND animal_id IS NOT NULL
    """
    appointment = execute_query(appointment_query, (adopter_id, consultant_id, adoption_date, slot_id), fetch=True)
    
    if not appointment or not appointment[0]['animal_id']:
        flash('Adoption appointment not found', 'danger')
        return redirect(url_for('proyas.my_consultations'))
    
    animal_id = appointment[0]['animal_id']
    
    # Get adoption and appointment details
    adopt_query = """
        SELECT ad.animal_id, ad.adopter_id, u.name as adopter_name, an.title as animal_name
        FROM Adopt ad
        INNER JOIN User u ON ad.adopter_id = u.id
        INNER JOIN Animal an ON ad.animal_id = an.id
        WHERE ad.adopter_id = %s AND ad.animal_id = %s
    """
    adoption = execute_query(adopt_query, (adopter_id, animal_id), fetch=True)
    
    if adoption:
        animal_id = adoption[0]['animal_id']
        adopter_name = adoption[0]['adopter_name']
        animal_name = adoption[0]['animal_name']
        
        # Update Adopt to approved
        update_query = "UPDATE Adopt SET approved = TRUE WHERE animal_id = %s AND adopter_id = %s"
        result = execute_query(update_query, (animal_id, adopter_id))
        
        if result is not None:
            # Send notification to adopter
            notif_title = "Adoption Approved!"
            notif_content = f"Your adoption for {animal_name} has been approved! The meeting is scheduled as confirmed."
            
            notif_id_query = "SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM Notification"
            notif_id = execute_query(notif_id_query, fetch=True)[0]['next_id']
            
            notif_insert = "INSERT INTO Notification (id, title, content, user_id) VALUES (%s, %s, %s, %s)"
            execute_query(notif_insert, (notif_id, notif_title, notif_content, adopter_id))
            
            flash(f'Adoption for {animal_name} approved!', 'success')
        else:
            flash('Failed to approve adoption', 'danger')
    else:
        flash('Adoption not found', 'danger')
    
    return redirect(url_for('proyas.my_consultations'))


@proyas_bp.route('/adoptions/reject/<int:adopter_id>/<int:consultant_id>/<adoption_date>/<int:slot_id>', methods=['POST'])
def reject_adoption(adopter_id, consultant_id, adoption_date, slot_id):
    """Consultant rejects an adoption appointment"""
    if 'user_id' not in session or session['user_id'] != consultant_id:
        flash('You do not have permission to reject this adoption', 'danger')
        return redirect(url_for('proyas.my_consultations'))
    
    # Get the animal_id from the appointment
    appointment_query = """
        SELECT animal_id FROM Appointment
        WHERE adopter_id = %s AND consultant_id = %s AND date = %s AND timeslot_id = %s AND animal_id IS NOT NULL
    """
    appointment = execute_query(appointment_query, (adopter_id, consultant_id, adoption_date, slot_id), fetch=True)
    
    if not appointment or not appointment[0]['animal_id']:
        flash('Adoption appointment not found', 'danger')
        return redirect(url_for('proyas.my_consultations'))
    
    animal_id = appointment[0]['animal_id']
    
    # Get adoption and appointment details
    adopt_query = """
        SELECT ad.animal_id, ad.adopter_id, u.name as adopter_name, an.title as animal_name
        FROM Adopt ad
        INNER JOIN User u ON ad.adopter_id = u.id
        INNER JOIN Animal an ON ad.animal_id = an.id
        WHERE ad.adopter_id = %s AND ad.animal_id = %s
    """
    adoption = execute_query(adopt_query, (adopter_id, animal_id), fetch=True)
    
    if adoption:
        animal_id = adoption[0]['animal_id']
        adopter_name = adoption[0]['adopter_name']
        animal_name = adoption[0]['animal_name']
        
        # Delete the adoption request
        delete_query = "DELETE FROM Adopt WHERE animal_id = %s AND adopter_id = %s"
        result = execute_query(delete_query, (animal_id, adopter_id))
        
        # Delete the appointment
        appointment_delete = "DELETE FROM Appointment WHERE adopter_id = %s AND consultant_id = %s AND date = %s AND timeslot_id = %s"
        execute_query(appointment_delete, (adopter_id, consultant_id, adoption_date, slot_id))
        
        if result is not None:
            # Send notification to adopter
            notif_title = "Adoption Request Rejected"
            notif_content = f"Your adoption request for {animal_name} has been rejected. Please contact admin for more information."
            
            notif_id_query = "SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM Notification"
            notif_id = execute_query(notif_id_query, fetch=True)[0]['next_id']
            
            notif_insert = "INSERT INTO Notification (id, title, content, user_id) VALUES (%s, %s, %s, %s)"
            execute_query(notif_insert, (notif_id, notif_title, notif_content, adopter_id))
            
            flash(f'Adoption request for {animal_name} rejected!', 'info')
        else:
            flash('Failed to reject adoption', 'danger')
    else:
        flash('Adoption not found', 'danger')
    
    return redirect(url_for('proyas.my_consultations'))