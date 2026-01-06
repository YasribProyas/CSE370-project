from flask import render_template, request, redirect, url_for, session, flash
from app.main import main_bp
from app.db import execute_query
from datetime import datetime

@main_bp.route('/')
def index():
    animals = execute_query("SELECT * FROM Animal ORDER BY id DESC LIMIT 10", fetch=True) or []
    
    posts = execute_query("""
        SELECT p.*, u.name as author_name 
        FROM Post p 
        LEFT JOIN User u ON p.admin_id = u.id 
        ORDER BY p.date DESC, p.time DESC 
        LIMIT 10
    """, fetch=True) or []
    

    categories = ['Cat', 'Dog', 'Bird', 'Other']
    category_counts = {}
    for category in categories:
        count_query = "SELECT COUNT(*) as count FROM Animal WHERE type = %s"
        result = execute_query(count_query, (category,), fetch=True)
        category_counts[category] = result[0]['count'] if result else 0
    
    return render_template('index.html', 
                         animals=animals, 
                         posts=posts,
                         categories=categories,
                         category_counts=category_counts)

@main_bp.route('/animals')
def animals():
    animal_type = request.args.get('type', '')
    
    if animal_type:
        query = "SELECT * FROM Animal WHERE type = %s ORDER BY id DESC"
        animals = execute_query(query, (animal_type,), fetch=True) or []
    else:
        query = "SELECT * FROM Animal ORDER BY id DESC"
        animals = execute_query(query, fetch=True) or []
    
    return render_template('animals.html', animals=animals, animal_type=animal_type)

@main_bp.route('/animal/<int:animal_id>')
def animal_detail(animal_id):
    query = "SELECT * FROM Animal WHERE id = %s"
    animals = execute_query(query, (animal_id,), fetch=True)
    
    if not animals:
        flash('Animal not found', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('animal_detail.html', animal=animals[0])
