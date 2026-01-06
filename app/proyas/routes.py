from flask import render_template, request, redirect, url_for, session, flash
from app.proyas import proyas_bp
from app.db import execute_query
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id') or not session.get('is_admin'):
            flash('You need admin access to view this page', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function






@proyas_bp.route('/')
def index():
    return render_template('proyas/index.html')

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
    
    return render_template('proyas/admin_dashboard.html',
                         animals_count=animals_count[0]['count'] if animals_count else 0,
                         users_count=users_count[0]['count'] if users_count else 0,
                         admins_count=admins_count[0]['count'] if admins_count else 0,
                         consultants_count=consultants_count[0]['count'] if consultants_count else 0,
                         animals=animals or [],
                         admins=admins or [],
                         consultants=consultants or [],
                         general_users=general_users or [])


@proyas_bp.route('/admin/animals')
@admin_required
def manage_animals():
    animals = execute_query("SELECT * FROM Animal", fetch=True)
    return render_template('proyas/manage_animals.html', animals=animals or [])

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
            return render_template('proyas/add_animal.html')
        
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
    
    return render_template('proyas/add_animal.html')

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
            return render_template('proyas/edit_animal.html', animal=animal)
        
        update_query = """UPDATE Animal SET title=%s, type=%s, breed=%s, color=%s, age=%s, 
                          sex=%s, size=%s, weight=%s, training=%s, description=%s, 
                          diet=%s, behaviour=%s, img_url=%s WHERE id=%s"""
        
        execute_query(update_query, (title, animal_type, breed, color, age, sex, size, weight,
                                     training, description, diet, behaviour, img_url, animal_id))
        
        flash('Animal updated successfully!', 'success')
        return redirect(url_for('proyas.manage_animals'))
    
    return render_template('proyas/edit_animal.html', animal=animal)

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
    return render_template('proyas/manage_users.html', users=users or [])

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
            return render_template('proyas/add_consultant.html', users=users or [])
        
        existing = execute_query("SELECT * FROM Consultant WHERE user_id = %s", (user_id,), fetch=True)
        
        if existing:
            flash('User is already a consultant', 'warning')
            return render_template('proyas/add_consultant.html', users=users or [])
        
        insert_query = """INSERT INTO Consultant (user_id, full_name, phone_no, address) 
                         VALUES (%s, %s, %s, %s)"""
        execute_query(insert_query, (user_id, full_name, phone_no, address))
        
        flash('Consultant added successfully!', 'success')
        return redirect(url_for('proyas.manage_users'))
    
    return render_template('proyas/add_consultant.html', users=users or [])


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
