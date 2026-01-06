from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app.shaj import shaj_bp
from app.db import execute_query
from datetime import datetime, timedelta
from functools import wraps


# ============== DONATION ROUTES ==============
@shaj_bp.route('/donation')
def donation():
    result = execute_query("SELECT SUM(amount) as total FROM Donation", fetch=True)
    total_donations = result[0]['total'] if result and result[0]['total'] else 0
    
    count_result = execute_query("SELECT COUNT(*) as count FROM Donation", fetch=True)
    donation_count = count_result[0]['count'] if count_result else 0
    
    recent_query = """
        SELECT d.*, u.name as donor_name 
        FROM Donation d 
        LEFT JOIN User u ON d.user_id = u.id 
        ORDER BY d.id DESC 
        LIMIT 10
    """
    recent_donations = execute_query(recent_query, fetch=True) or []
    
    return render_template('donation.html', 
                         total_donations=total_donations,
                         donation_count=donation_count,
                         recent_donations=recent_donations)

@shaj_bp.route('/donate', methods=['GET', 'POST'])
def donate():
    if 'user_id' not in session:
        flash('Please login to make a donation', 'warning')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        amount = request.form.get('amount')
        method = request.form.get('method')
        trx_id = request.form.get('trx_id')
        
        # Validate amount
        try:
            amount = float(amount)
            if amount <= 0:
                flash('Amount must be greater than 0', 'danger')
                return render_template('donate.html')
        except (ValueError, TypeError):
            flash('Invalid amount', 'danger')
            return render_template('donate.html')
        
        # Validate required fields
        if not method:
            flash('Please select a payment method', 'danger')
            return render_template('donate.html')
        
        if not trx_id:
            flash('Transaction ID is required', 'danger')
            return render_template('donate.html')
        
        # Get next donation ID
        id_query = "SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM Donation"
        result = execute_query(id_query, fetch=True)
        next_id = result[0]['next_id'] if result else 1
        
        # Insert donation
        insert_query = "INSERT INTO Donation (id, amount, method, trx_id, user_id) VALUES (%s, %s, %s, %s, %s)"
        result = execute_query(insert_query, (next_id, amount, method, trx_id, session['user_id']))
        
        if result is not None:
            flash(f'Thank you for your generous donation of {amount:.2f} taka!', 'success')
            return redirect(url_for('shaj.donation'))
        else:
            flash('Donation failed. Please try again.', 'danger')
    
    return render_template('donate.html')

# ============== ADOPTION ROUTES ==============
@shaj_bp.route('/adopt/<int:animal_id>', methods=['GET', 'POST'])
def adopt_animal(animal_id):
    if 'user_id' not in session:
        flash('Please login to request adoption', 'warning')
        return redirect(url_for('auth.login'))
    
    # Get animal details
    animal_query = "SELECT * FROM Animal WHERE id = %s"
    animals = execute_query(animal_query, (animal_id,), fetch=True)
    
    if not animals:
        flash('Animal not found', 'danger')
        return redirect(url_for('main.animals'))
    
    animal = animals[0]
    
    # Check if user is already an adopter
    check_adopter = "SELECT * FROM Adopter WHERE user_id = %s"
    adopter = execute_query(check_adopter, (session['user_id'],), fetch=True)
    
    # Check if already requested adoption for this animal
    check_adoption = "SELECT * FROM Adopt WHERE animal_id = %s AND adopter_id = %s"
    existing_adoption = execute_query(check_adoption, (animal_id, session['user_id']), fetch=True)
    
    if existing_adoption:
        flash('You have already requested adoption for this animal', 'info')
        return redirect(url_for('main.animal_detail', animal_id=animal_id))
    
    if request.method == 'POST':
        # Get form data
        full_name = request.form.get('full_name')
        address = request.form.get('address')
        phone_no = request.form.get('phone_no')
        marital_status = request.form.get('marital_status')
        job = request.form.get('job')
        payment_method = request.form.get('payment_method')
        trx_id = request.form.get('trx_id')
        
        # Validate required fields
        if not all([full_name, address, phone_no, marital_status, job, payment_method]):
            flash('All fields are required', 'danger')
            return render_template('adopt_form.html', animal=animal, adopter=adopter[0] if adopter else None)
        
        # Validate transaction ID for non-cash payments
        if payment_method != 'Cash on Delivery' and not trx_id:
            flash('Transaction ID is required for online payments', 'danger')
            return render_template('adopt_form.html', animal=animal, adopter=adopter[0] if adopter else None)
        
        # If user is not an adopter, create adopter record
        if not adopter or len(adopter) == 0:
            insert_adopter = """
                INSERT INTO Adopter (user_id, full_name, address, phone_no, marital_status, job) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            result = execute_query(insert_adopter, (session['user_id'], full_name, address, phone_no, marital_status, job))
            
            if result is None:
                flash('Failed to create adopter profile', 'danger')
                return render_template('adopt_form.html', animal=animal, adopter=None)
        else:
            # Update adopter information if needed
            update_adopter = """
                UPDATE Adopter 
                SET full_name = %s, address = %s, phone_no = %s, marital_status = %s, job = %s 
                WHERE user_id = %s
            """
            execute_query(update_adopter, (full_name, address, phone_no, marital_status, job, session['user_id']))
        
        # Create adoption request
        insert_adoption = """
            INSERT INTO Adopt (animal_id, adopter_id, adoption_date, approved) 
            VALUES (%s, %s, %s, %s)
        """
        current_date = datetime.now().date()
        result = execute_query(insert_adoption, (animal_id, session['user_id'], current_date, False))
        
        if result is not None:
            flash(f'Adoption request submitted successfully! Delivery charge: 100 taka via {payment_method}', 'success')
            return redirect(url_for('shaj.my_adoptions'))
        else:
            flash('Failed to submit adoption request', 'danger')
    
    # Pre-fill form if user is already an adopter
    return render_template('adopt_form.html', animal=animal, adopter=adopter[0] if adopter else None)

@shaj_bp.route('/my-adoptions')
def my_adoptions():
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('auth.login'))
    
    # Get user's adoption requests
    query = """
        SELECT a.*, an.title, an.type, an.breed, an.img_url, an.age, an.sex
        FROM Adopt a
        LEFT JOIN Animal an ON a.animal_id = an.id
        WHERE a.adopter_id = %s
        ORDER BY a.adoption_date DESC
    """
    adoptions = execute_query(query, (session['user_id'],), fetch=True) or []
    
    return render_template('my_adoptions.html', adoptions=adoptions)

@shaj_bp.route('/cancel-adoption/<int:animal_id>', methods=['POST'])
def cancel_adoption(animal_id):
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('auth.login'))
    
    # Check if adoption is approved
    check_query = "SELECT approved FROM Adopt WHERE animal_id = %s AND adopter_id = %s"
    adoption = execute_query(check_query, (animal_id, session['user_id']), fetch=True)
    
    if adoption and adoption[0]['approved']:
        flash('Cannot cancel an approved adoption. Please contact admin.', 'danger')
        return redirect(url_for('shaj.my_adoptions'))
    
    # Delete adoption request
    delete_query = "DELETE FROM Adopt WHERE animal_id = %s AND adopter_id = %s"
    result = execute_query(delete_query, (animal_id, session['user_id']))
    
    if result is not None:
        flash('Adoption request cancelled successfully', 'info')
    else:
        flash('Failed to cancel adoption request', 'danger')
    
    return redirect(url_for('shaj.my_adoptions'))


# ============== ADOPTION APPOINTMENT ROUTES ==============
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id') or not session.get('is_admin'):
            flash('You need admin access to view this page', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@shaj_bp.route('/admin/adoptions')
@admin_required
def admin_adoptions():
    """Admin view of all pending adoption requests"""
    query = """
        SELECT a.*, an.title, an.breed, an.type, u.name as adopter_name, ad.full_name, ad.phone_no
        FROM Adopt a
        INNER JOIN Animal an ON a.animal_id = an.id
        INNER JOIN Adopter ad ON a.adopter_id = ad.user_id
        INNER JOIN User u ON a.adopter_id = u.id
        WHERE a.approved = FALSE
        ORDER BY a.adoption_date DESC
    """
    pending_adoptions = execute_query(query, fetch=True) or []
    return render_template('/admin_adoptions.html', adoptions=pending_adoptions)


@shaj_bp.route('/admin/adoptions/set-appointment/<int:animal_id>/<int:adopter_id>', methods=['GET', 'POST'])
@admin_required
def set_adoption_appointment(animal_id, adopter_id):
    """Admin sets appointment for adoption (choose consultant, date, slot, and link all at once)"""
    if request.method == 'POST':
        consultant_id = request.form.get('consultant_id')
        selected_date = request.form.get('adoption_date')
        selected_slot = request.form.get('timeslot_id')
        link = request.form.get('link', '0')
        
        if not all([consultant_id, selected_date, selected_slot]):
            flash('Please select consultant, date, and time slot', 'danger')
            return redirect(url_for('shaj.admin_adoptions'))
        
        try:
            consultant_id = int(consultant_id)
            selected_slot = int(selected_slot)
        except ValueError:
            flash('Invalid consultant or time slot', 'danger')
            return redirect(url_for('shaj.admin_adoptions'))
        
        # Check if adoption exists
        adoption_check = "SELECT * FROM Adopt WHERE animal_id = %s AND adopter_id = %s"
        adoption = execute_query(adoption_check, (animal_id, adopter_id), fetch=True)
        
        if not adoption:
            flash('Adoption request not found', 'danger')
            return redirect(url_for('shaj.admin_adoptions'))
        
        # Check if appointment already exists for this adoption
        appointment_check = "SELECT * FROM Appointment WHERE adopter_id = %s AND consultant_id = %s AND timeslot_id = %s AND date = %s"
        existing = execute_query(appointment_check, (adopter_id, consultant_id, selected_slot, selected_date), fetch=True)
        
        if existing:
            flash('This appointment slot is already booked', 'danger')
            return redirect(url_for('shaj.admin_adoptions'))
        
        # Insert into Appointment table for adoption appointment
        insert_query = """
            INSERT INTO Appointment (adopter_id, consultant_id, timeslot_id, date, link) 
            VALUES (%s, %s, %s, %s, %s)
        """
        result = execute_query(insert_query, (adopter_id, consultant_id, selected_slot, selected_date, link))
        
        if result is not None:
            # Get details for notifications
            adopter_query = "SELECT u.name as adopter_name FROM User u WHERE u.id = %s"
            adopter = execute_query(adopter_query, (adopter_id,), fetch=True)
            
            consultant_query = "SELECT u.name as consultant_name FROM User u WHERE u.id = %s"
            consultant = execute_query(consultant_query, (consultant_id,), fetch=True)
            
            animal_query = "SELECT title FROM Animal WHERE id = %s"
            animal = execute_query(animal_query, (animal_id,), fetch=True)
            
            slot_query = "SELECT slot FROM TimeSlot WHERE id = %s"
            slot = execute_query(slot_query, (selected_slot,), fetch=True)
            
            formatted_date = datetime.strptime(selected_date, '%Y-%m-%d').strftime('%d %b %Y')
            slot_time = slot[0]['slot'] if slot else 'N/A'
            
            # Create notification for adopter
            adopter_notif_title = "Adoption Appointment Scheduled!"
            adopter_notif_content = f"Your adoption appointment for {animal[0]['title']} has been scheduled with {consultant[0]['consultant_name']}. Date: {formatted_date}, Time: {slot_time}. Meeting Link: {link}"
            
            adopter_notif_id_query = "SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM Notification"
            adopter_notif_id = execute_query(adopter_notif_id_query, fetch=True)[0]['next_id']
            
            adopter_insert = "INSERT INTO Notification (id, title, content, user_id) VALUES (%s, %s, %s, %s)"
            execute_query(adopter_insert, (adopter_notif_id, adopter_notif_title, adopter_notif_content, adopter_id))
            
            # Create notification for consultant
            consultant_notif_title = "New Adoption Appointment!"
            consultant_notif_content = f"Adoption appointment scheduled with {adopter[0]['adopter_name']} for {animal[0]['title']}. Date: {formatted_date}, Time: {slot_time}. Meeting Link: {link}"
            
            consultant_notif_id_query = "SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM Notification"
            consultant_notif_id = execute_query(consultant_notif_id_query, fetch=True)[0]['next_id']
            
            consultant_insert = "INSERT INTO Notification (id, title, content, user_id) VALUES (%s, %s, %s, %s)"
            execute_query(consultant_insert, (consultant_notif_id, consultant_notif_title, consultant_notif_content, consultant_id))
            
            flash('Adoption appointment set and notifications sent!', 'success')
        else:
            flash('Failed to set appointment', 'danger')
        
        return redirect(url_for('shaj.admin_adoptions'))
    
    # GET request - show form to set appointment
    animal_query = "SELECT * FROM Animal WHERE id = %s"
    animal = execute_query(animal_query, (animal_id,), fetch=True)
    
    adopter_query = "SELECT * FROM User WHERE id = %s"
    adopter = execute_query(adopter_query, (adopter_id,), fetch=True)
    
    consultants_query = "SELECT u.id, u.name FROM User u INNER JOIN Consultant c ON u.id = c.user_id ORDER BY u.name"
    consultants = execute_query(consultants_query, fetch=True) or []
    
    timeslots_query = "SELECT * FROM TimeSlot ORDER BY id"
    timeslots = execute_query(timeslots_query, fetch=True) or []
    
    return render_template('/adoption_appointment.html', 
                          animal=animal[0] if animal else None,
                          adopter=adopter[0] if adopter else None,
                          consultants=consultants,
                          timeslots=timeslots)
