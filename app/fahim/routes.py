from datetime import datetime
from flask import flash, redirect, render_template, request, session, url_for
from app.db import execute_query
from app.fahim import fahim_bp
import os
from werkzeug.utils import secure_filename


# =========================
# ADMIN POSTS
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


@fahim_bp.route('/post/create', methods=['GET', 'POST'])
def create_post():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Admin access required', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        content = request.form.get('content')
        image = request.files.get('image')

        if not content:
            flash('Post content is required', 'danger')
            return redirect(url_for('fahim.create_post'))

        img_url = None
        if image and image.filename:
            filename = secure_filename(image.filename)
            upload_path = os.path.join('app/static/uploads', filename)
            image.save(upload_path)
            img_url = f'/static/uploads/{filename}'

        now = datetime.now()
        execute_query(
            """
            INSERT INTO Post (content, img_url, date, time, admin_id)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (content, img_url, now.date(), now.time(), session['user_id'])
        )

        flash('Post published successfully!', 'success')
        return redirect(url_for('fahim.posts'))

    return render_template('create_post.html')


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
        return redirect(url_for('fahim.posts'))

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
    existing = execute_query(
        "SELECT 1 FROM Post_Like WHERE user_id=%s AND post_id=%s",
        (user_id, post_id),
        fetch=True
    )

    if existing:
        execute_query(
            "DELETE FROM Post_Like WHERE user_id=%s AND post_id=%s",
            (user_id, post_id)
        )
    else:
        now = datetime.now()
        execute_query(
            "INSERT INTO Post_Like (user_id, post_id, date, time) VALUES (%s, %s, %s, %s)",
            (user_id, post_id, now.date(), now.time())
        )

    return redirect(request.referrer)


@fahim_bp.route('/post/<int:post_id>/comment', methods=['POST'])
def comment_post(post_id):
    if 'user_id' not in session:
        flash('Please login to comment', 'warning')
        return redirect(url_for('auth.login'))

    content = request.form.get('content')
    if not content:
        flash('Comment cannot be empty', 'danger')
        return redirect(url_for('fahim.post_detail', post_id=post_id))

    now = datetime.now()
    execute_query(
        """
        INSERT INTO Post_Comment (content, date, time, user_id, post_id)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (content, now.date(), now.time(), session['user_id'], post_id)
    )

    flash('Comment added!', 'success')
    return redirect(url_for('fahim.post_detail', post_id=post_id))


# =========================
# USER BLOG SYSTEM
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
    existing = execute_query(
        "SELECT 1 FROM Blog_Like WHERE user_id=%s AND blog_id=%s",
        (user_id, blog_id),
        fetch=True
    )

    if existing:
        execute_query(
            "DELETE FROM Blog_Like WHERE user_id=%s AND blog_id=%s",
            (user_id, blog_id)
        )
    else:
        now = datetime.now()
        execute_query(
            "INSERT INTO Blog_Like (user_id, blog_id, date, time) VALUES (%s, %s, %s, %s)",
            (user_id, blog_id, now.date(), now.time())
        )

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

    now = datetime.now()
    execute_query(
        """
        INSERT INTO Blog_Comment (content, date, time, user_id, blog_id)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (content, now.date(), now.time(), session['user_id'], blog_id)
    )

    flash('Comment added!', 'success')
    return redirect(url_for('fahim.blog_detail', blog_id=blog_id))


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
        if image and image.filename:
            filename = secure_filename(image.filename)
            upload_path = os.path.join('app/static/uploads', filename)
            image.save(upload_path)
            img_url = f'/static/uploads/{filename}'

        now = datetime.now()
        execute_query(
            """
            INSERT INTO Blog (title, content, img_url, date, time, user_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (title, content, img_url, now.date(), now.time(), session['user_id'])
        )

        flash('Blog posted successfully!', 'success')
        return redirect(url_for('fahim.blogs'))

    return render_template('create_blog.html')