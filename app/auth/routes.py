from flask import render_template, request, redirect, url_for, session, flash
from app.auth import auth_bp
from app.db import execute_query
from werkzeug.security import generate_password_hash, check_password_hash

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        users = execute_query("SELECT * FROM User WHERE email = %s", (email,), fetch=True)
        
        if users and len(users) > 0 and password and len(password) > 0:
            user = users[0]
            if check_password_hash(user['pass'], password):
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_email'] = user['email']
                
                #todo: also for adopter and consultant. maybe implement match case
                admin_query = "SELECT * FROM Admin WHERE user_id = %s"
                admin = execute_query(admin_query, (user['id'],), fetch=True)
                session['is_admin'] = len(admin) > 0 if admin else False
                
                flash('Login successful! :D', 'success')
                return redirect(url_for('main.index'))
            else:
                flash('Invalid email or password', 'danger')
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not name or not email or not password:
            flash('All fields are required', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        check_query = "SELECT * FROM User WHERE email = %s"
        existing = execute_query(check_query, (email,), fetch=True)
        
        if existing and len(existing) > 0:
            flash('Email already registered', 'danger')
            return render_template('register.html')
        
        hashed_password = generate_password_hash(password)
        
        id_query = "SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM User"
        result = execute_query(id_query, fetch=True)
        next_id = result[0]['next_id'] if result else 1
        
        insert_query = "INSERT INTO User (id, name, email, pass) VALUES (%s, %s, %s, %s)"
        result = execute_query(insert_query, (next_id, name, email, hashed_password))
        
        if result is not None:
            general_query = "INSERT INTO GeneralUser (user_id) VALUES (%s)"
            execute_query(general_query, (next_id,))
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Registration failed. Please try again.', 'danger')
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out T-T', 'info')
    return redirect(url_for('main.index'))
