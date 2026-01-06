from flask import render_template, request, redirect, url_for, session, flash
from app.shaj import shaj_bp
from app.db import execute_query
from datetime import datetime


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



# ============== CONSULTATION ROUTES ==============

@shaj_bp.route('/consultants')
def consultants():
    """Display all available consultants"""
    query = """
        SELECT c.*, u.name as user_name, u.email 
        FROM Consultant c 
        LEFT JOIN User u ON c.user_id = u.id
        ORDER BY c.user_id
    """
    consultants = execute_query(query, fetch=True) or []
    
    return render_template('consultants.html', consultants=consultants)

@shaj_bp.route('/consultant/<int:consultant_id>')
def consultant_detail(consultant_id):
    """Display consultant details"""
    query = """
        SELECT c.*, u.name as user_name, u.email 
        FROM Consultant c 
        LEFT JOIN User u ON c.user_id = u.id
        WHERE c.user_id = %s
    """
    consultants = execute_query(query, (consultant_id,), fetch=True)
    
    if not consultants:
        flash('Consultant not found', 'danger')
        return redirect(url_for('shaj.consultants'))
    # Determine if current user is a registered adopter (used by template to show Book button)
    is_adopter = False
    if 'user_id' in session:
        check_adopter = "SELECT * FROM Adopter WHERE user_id = %s"
        adopter = execute_query(check_adopter, (session['user_id'],), fetch=True)
        is_adopter = bool(adopter)

    return render_template('consultant_detail.html', consultant=consultants[0], is_adopter=is_adopter)

@shaj_bp.route('/consultation/book/<int:consultant_id>', methods=['GET', 'POST'])
def book_appointment(consultant_id):
    """Book an appointment with a consultant"""
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('auth.login'))
    
    # Get consultant info
    consultant_query = """
        SELECT c.*, u.name as user_name, u.email
        FROM Consultant c 
        LEFT JOIN User u ON c.user_id = u.id
        WHERE c.user_id = %s
    """
    consultants = execute_query(consultant_query, (consultant_id,), fetch=True)
    
    if not consultants:
        flash('Consultant not found', 'danger')
        return redirect(url_for('shaj.consultants'))
    
    if request.method == 'POST':
        # Get form data
        full_name = request.form.get('full_name')
        address = request.form.get('address')
        phone_no = request.form.get('phone_no')
        appointment_date = request.form.get('appointment_date')
        time_slot = request.form.get('time_slot')
        reason = request.form.get('reason')
        method = request.form.get('method')  # WhatsApp/Google Meet/Zoom
        payment_method = request.form.get('payment_method')
        trx_id = request.form.get('trx_id')
        
        # Validate required fields
        if not all([full_name, address, phone_no, appointment_date, time_slot, reason, method, payment_method]):
            flash('All fields are required', 'danger')
            return render_template('book_consultation.html', consultant=consultants[0])
        
        # Validate transaction ID for non-cash payments
        if payment_method != 'Cash' and not trx_id:
            flash('Transaction ID is required for online payments', 'danger')
            return render_template('book_consultation.html', consultant=consultants[0])
        
        # Get next appointment ID
        id_query = "SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM ConsultationAppointment"
        result = execute_query(id_query, fetch=True)
        next_id = result[0]['next_id'] if result else 1
        
        # Insert appointment
        insert_query = """
            INSERT INTO ConsultationAppointment 
            (id, user_id, consultant_id, full_name, address, phone_no, appointment_date, 
             time_slot, reason, consultation_method, payment_method, trx_id, status, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        current_datetime = datetime.now()
        result = execute_query(insert_query, (
            next_id, session['user_id'], consultant_id, full_name, address, phone_no,
            appointment_date, time_slot, reason, method, payment_method, trx_id,
            'pending', current_datetime
        ))
        
        if result is not None:
            flash('Appointment booked successfully!', 'success')
            return redirect(url_for('shaj.appointment_confirmation', appointment_id=next_id))
        else:
            flash('Booking failed. Please try again.', 'danger')
    
    return render_template('book_consultation.html', consultant=consultants[0])

@shaj_bp.route('/consultation/confirmation/<int:appointment_id>')
def appointment_confirmation(appointment_id):
    """Display appointment confirmation"""
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('auth.login'))
    
    query = """
        SELECT ca.*, c.full_name as consultant_name, c.phone_no as consultant_phone,
               u.email as consultant_email
        FROM ConsultationAppointment ca
        LEFT JOIN Consultant c ON ca.consultant_id = c.user_id
        LEFT JOIN User u ON c.user_id = u.id
        WHERE ca.id = %s AND ca.user_id = %s
    """
    appointments = execute_query(query, (appointment_id, session['user_id']), fetch=True)
    
    if not appointments:
        flash('Appointment not found', 'danger')
        return redirect(url_for('shaj.my_consultations'))
    
    return render_template('consultation_confirmation.html', appointment=appointments[0])

@shaj_bp.route('/consultation/my-appointments')
def my_consultations():
    """Display user's consultation appointments"""
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('auth.login'))
    
    query = """
        SELECT ca.*, 
               c.full_name as consultant_name, c.phone_no as consultant_phone,
               u.email as consultant_email
        FROM ConsultationAppointment ca
        LEFT JOIN Consultant c ON ca.consultant_id = c.user_id
        LEFT JOIN User u ON c.user_id = u.id
        WHERE ca.user_id = %s
        ORDER BY ca.appointment_date DESC, ca.time_slot DESC
    """
    appointments = execute_query(query, (session['user_id'],), fetch=True) or []
    
    return render_template('my_consultations.html', appointments=appointments)

@shaj_bp.route('/consultation/cancel/<int:appointment_id>', methods=['POST'])
def cancel_consultation(appointment_id):
    """Cancel a consultation appointment"""
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('auth.login'))
    
    # Check if appointment exists and belongs to user
    check_query = """
        SELECT * FROM ConsultationAppointment 
        WHERE id = %s AND user_id = %s
    """
    appointment = execute_query(check_query, (appointment_id, session['user_id']), fetch=True)
    
    if not appointment:
        flash('Appointment not found', 'danger')
        return redirect(url_for('shaj.my_consultations'))
    
    # Check if appointment is already confirmed
    if appointment[0]['status'] == 'confirmed':
        flash('Cannot cancel a confirmed appointment. Please contact support.', 'warning')
        return redirect(url_for('shaj.my_consultations'))
    
    # Update status to cancelled
    update_query = """
        UPDATE ConsultationAppointment 
        SET status = 'cancelled', cancelled_at = %s
        WHERE id = %s
    """
    result = execute_query(update_query, (datetime.now(), appointment_id))
    
    if result is not None:
        # In a real application, you would initiate refund process here
        flash('Appointment cancelled successfully. Refund will be processed within 3-5 business days.', 'info')
    else:
        flash('Failed to cancel appointment', 'danger')
    
    return redirect(url_for('shaj.my_consultations'))