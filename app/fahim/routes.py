from datetime import datetime
from flask import flash, redirect, render_template, request, session, url_for
from app.db import execute_query
from app.fahim import fahim_bp
import os
from werkzeug.utils import secure_filename


# =========================
# ADMIN POSTS (ALREADY EXISTING)
# =========================

@fahim_bp.route('/posts')
def posts():
    query = """
        SELECT p.*, u.name AS author_name,
               (SELECT COUNT(*) FROM Post_Like WHERE post_id = p.id) AS like_count,
               (SELECT COUNT(*) FROM Post_Comment WHERE post_id = p.id) AS comment_count
        FROM Post p
        LEFT JOIN User u ON p.admin_id = u.id
        ORDER BY p.date DESC, p.time DESC
    """
    posts = execute_query(query, fetch=True) or []
    return render_template('posts.html', posts=posts)


@fahim_bp.route('/post/<int:post_id>')
def post_detail(post_id):
    post_query = """
        SELECT p.*, u.name AS author_name,
               (SELECT COUNT(*) FROM Post_Like WHERE post_id = p.id) AS like_count
        FROM Post p
        LEFT JOIN User u ON p.admin_id = u.id
        WHERE p.id = %s
    """
    posts = execute_query(post_query, (post_id,), fetch=True)

    if not posts:
        flash('Post not found', 'danger')
        return redirect(url_for('main.posts'))

    comments_query = """
        SELECT pc.*, u.name AS author_name
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

    check_query = "SELECT 1 FROM Post_Like WHERE user_id = %s AND post_id = %s"
    existing = execute_query(check_query, (user_id, post_id), fetch=True)

    if existing:
        delete_query = "DELETE FROM Post_Like WHERE user_id = %s AND post_id = %s"
        execute_query(delete_query, (user_id, post_id))
        flash('Post unliked', 'info')
    else:
        insert_query = """
            INSERT INTO Post_Like (user_id, post_id, date, time)
            VALUES (%s, %s, %s, %s)
        """
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

    insert_query = """
        INSERT INTO Post_Comment (content, date, time, user_id, post_id)
        VALUES (%s, %s, %s, %s, %s)
    """
    now = datetime.now()
    execute_query(
        insert_query,
        (content, now.date(), now.time(), session['user_id'], post_id)
    )

    flash('Comment added!', 'success')
    return redirect(url_for('main.post_detail', post_id=post_id))


# =========================
# USER BLOG SYSTEM (UPDATED WITH LOVE REACT)
# =========================

@fahim_bp.route('/blogs')
def blogs():
    query = """
        SELECT b.*, u.name AS author_name,
               (SELECT COUNT(*) FROM Blog_Comment WHERE blog_id = b.id) AS comment_count,
               (SELECT COUNT(*) FROM Blog_Like WHERE blog_id = b.id) AS like_count
        FROM Blog b
        LEFT JOIN User u ON b.user_id = u.id
        ORDER BY b.date DESC, b.time DESC
    """
    blogs = execute_query(query, fetch=True) or []
    return render_template('blogs.html', blogs=blogs)


@fahim_bp.route('/blog/<int:blog_id>')
def blog_detail(blog_id):
    blog_query = """
        SELECT b.*, u.name AS author_name,
               (SELECT COUNT(*) FROM Blog_Like WHERE blog_id = b.id) AS like_count
        FROM Blog b
        LEFT JOIN User u ON b.user_id = u.id
        WHERE b.id = %s
    """
    blogs = execute_query(blog_query, (blog_id,), fetch=True)

    if not blogs:
        flash('Blog not found', 'danger')
        return redirect(url_for('fahim.blogs'))

    comment_query = """
        SELECT bc.*, u.name AS author_name
        FROM Blog_Comment bc
        LEFT JOIN User u ON bc.user_id = u.id
        WHERE bc.blog_id = %s
        ORDER BY bc.date DESC, bc.time DESC
    """
    comments = execute_query(comment_query, (blog_id,), fetch=True) or []

    return render_template('blog_detail.html', blog=blogs[0], comments=comments)


@fahim_bp.route('/blog/<int:blog_id>/like', methods=['POST'])
def like_blog(blog_id):
    if 'user_id' not in session:
        flash('Please login to react', 'warning')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    check_query = "SELECT 1 FROM Blog_Like WHERE user_id = %s AND blog_id = %s"
    existing = execute_query(check_query, (user_id, blog_id), fetch=True)

    if existing:
        execute_query(
            "DELETE FROM Blog_Like WHERE user_id = %s AND blog_id = %s",
            (user_id, blog_id)
        )
        flash('Love removed', 'info')
    else:
        now = datetime.now()
        execute_query(
            "INSERT INTO Blog_Like (user_id, blog_id, date, time) VALUES (%s, %s, %s, %s)",
            (user_id, blog_id, now.date(), now.time())
        )
        flash('Loved ❤️', 'success')

    return redirect(request.referrer or url_for('fahim.blogs'))


@fahim_bp.route('/blog/<int:blog_id>/comment', methods=['POST'])
def comment_blog(blog_id):
    if 'user_id' not in session:
        flash('Please login to comment', 'warning')
        return redirect(url_for('auth.login'))

    content = request.form.get('content')
    if not content:
        flash('Comment cannot be empty', 'danger')
        return redirect(url_for('fahim.blog_detail', blog_id=blog_id))

    insert_query = """
        INSERT INTO Blog_Comment (content, date, time, user_id, blog_id)
        VALUES (%s, %s, %s, %s, %s)
    """
    now = datetime.now()
    execute_query(
        insert_query,
        (content, now.date(), now.time(), session['user_id'], blog_id)
    )

    flash('Comment added!', 'success')
    return redirect(url_for('fahim.blog_detail', blog_id=blog_id))


# =========================
# BLOG CREATE (IMAGE UPLOAD)
# =========================

@fahim_bp.route('/blog/create', methods=['GET', 'POST'])
def create_blog():
    if 'user_id' not in session:
        flash('Please login to create blog', 'warning')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        image = request.files.get('image')

        if not title or not content:
            flash('Title and content are required', 'danger')
            return redirect(url_for('fahim.create_blog'))

        img_url = None

        if image and image.filename != '':
            filename = secure_filename(image.filename)
            upload_path = os.path.join('app/static/uploads', filename)
            image.save(upload_path)
            img_url = f'/static/uploads/{filename}'

        insert_query = """
            INSERT INTO Blog (title, content, img_url, date, time, user_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        now = datetime.now()
        execute_query(
            insert_query,
            (title, content, img_url, now.date(), now.time(), session['user_id'])
        )

        flash('Blog posted successfully!', 'success')
        return redirect(url_for('fahim.blogs'))

    return render_template('create_blog.html')


# =========================
# BLOG EDIT
# =========================

@fahim_bp.route('/blog/<int:blog_id>/edit', methods=['GET', 'POST'])
def edit_blog(blog_id):
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('auth.login'))

    blogs = execute_query("SELECT * FROM Blog WHERE id = %s", (blog_id,), fetch=True)
    if not blogs:
        flash('Blog not found', 'danger')
        return redirect(url_for('fahim.blogs'))

    blog = blogs[0]

    if blog['user_id'] != session['user_id']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('fahim.blogs'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        image = request.files.get('image')

        img_url = blog['img_url']

        if image and image.filename != '':
            filename = secure_filename(image.filename)
            upload_path = os.path.join('app/static/uploads', filename)
            image.save(upload_path)
            img_url = f'/static/uploads/{filename}'

        execute_query(
            "UPDATE Blog SET title=%s, content=%s, img_url=%s WHERE id=%s",
            (title, content, img_url, blog_id)
        )

        flash('Blog updated successfully!', 'success')
        return redirect(url_for('fahim.blog_detail', blog_id=blog_id))

    return render_template('edit_blog.html', blog=blog)


# =========================
# BLOG DELETE
# =========================

@fahim_bp.route('/blog/<int:blog_id>/delete', methods=['POST'])
def delete_blog(blog_id):
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('auth.login'))

    blogs = execute_query("SELECT * FROM Blog WHERE id = %s", (blog_id,), fetch=True)
    if not blogs:
        flash('Blog not found', 'danger')
        return redirect(url_for('fahim.blogs'))

    blog = blogs[0]

    if blog['user_id'] != session['user_id']:
        flash('Unauthorized delete attempt', 'danger')
        return redirect(url_for('fahim.blogs'))

    execute_query("DELETE FROM Blog WHERE id = %s", (blog_id,))
    flash('Blog deleted successfully!', 'success')
    return redirect(url_for('fahim.blogs'))
