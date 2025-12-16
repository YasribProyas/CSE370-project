from datetime import datetime
from flask import flash, redirect, render_template, request, session, url_for
from app.db import execute_query
from app.fahim import fahim_bp

@fahim_bp.route('/posts')
def posts():
    query = """
        SELECT p.*, u.name as author_name,
               (SELECT COUNT(*) FROM Post_Like WHERE post_id = p.id) as like_count,
               (SELECT COUNT(*) FROM Post_Comment WHERE post_id = p.id) as comment_count
        FROM Post p
        LEFT JOIN User u ON p.admin_id = u.id
        ORDER BY p.date DESC, p.time DESC
    """
    posts = execute_query(query, fetch=True) or []
    
    return render_template('posts.html', posts=posts)

@fahim_bp.route('/post/<int:post_id>')
def post_detail(post_id):
    post_query = """
        SELECT p.*, u.name as author_name,
               (SELECT COUNT(*) FROM Post_Like WHERE post_id = p.id) as like_count
        FROM Post p
        LEFT JOIN User u ON p.admin_id = u.id
        WHERE p.id = %s
    """
    posts = execute_query(post_query, (post_id,), fetch=True)
    
    if not posts:
        flash('Post not found', 'danger')
        return redirect(url_for('main.posts'))
    
    comments_query = """
        SELECT pc.*, u.name as author_name
        FROM Post_Comment pc
        LEFT JOIN User u ON pc.user_id = u.id
        WHERE pc.post_id = %s
        ORDER BY pc.date DESC, pc.time DESC
    """
    comments = execute_query(comments_query, (post_id,), fetch=True) or []
    
    return render_template('post_detail.html', post=posts[0], comments=comments)

@fahim_bp.route('/post/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    if 'user_id' not in session:
        flash('Please login to like posts', 'warning')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    check_query = "SELECT * FROM Post_Like WHERE user_id = %s AND post_id = %s"
    existing = execute_query(check_query, (user_id, post_id), fetch=True)
    
    if existing:
        delete_query = "DELETE FROM Post_Like WHERE user_id = %s AND post_id = %s"
        execute_query(delete_query, (user_id, post_id))
        flash('Post unliked', 'info')
    else:
        insert_query = "INSERT INTO Post_Like (user_id, post_id, date, time) VALUES (%s, %s, %s, %s)"
        now = datetime.now()
        execute_query(insert_query, (user_id, post_id, now.date(), now.time()))
        flash('Post liked!', 'success')
    
    return redirect(url_for('main.post_detail', post_id=post_id))

@fahim_bp.route('/post/<int:post_id>/comment', methods=['POST'])
def comment_post(post_id):
    if 'user_id' not in session:
        flash('Please login to comment', 'warning')
        return redirect(url_for('auth.login'))
    
    content = request.form.get('content')
    if not content:
        flash('Comment cannot be empty', 'danger')
        return redirect(url_for('main.post_detail', post_id=post_id))
    
    id_query = "SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM Post_Comment"
    result = execute_query(id_query, fetch=True)
    next_id = result[0]['next_id'] if result else 1
    
    insert_query = "INSERT INTO Post_Comment (id, content, date, time, user_id, post_id) VALUES (%s, %s, %s, %s, %s, %s)"
    now = datetime.now()
    execute_query(insert_query, (next_id, content, now.date(), now.time(), session['user_id'], post_id))
    
    flash('Comment added!', 'success')
    return redirect(url_for('main.post_detail', post_id=post_id))
