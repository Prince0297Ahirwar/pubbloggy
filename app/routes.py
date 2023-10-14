from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import RegistrationForm, LoginForm,BlogForm,UpdateBlogForm,CommentForm
from app.models import User, Blog, Comment, LikeDislike
from flask_login import current_user, login_user, logout_user, login_required

@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = Blog.query.all()
    return render_template('index.html', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        print('User registration successful')
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='Profile')




@app.route('/create_blog', methods=['GET', 'POST'])
@login_required
def create_blog():
    form = BlogForm()
    if form.validate_on_submit():
        post = Blog(title=form.title.data, content=form.content.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_blog.html', form=form)

@app.route('/my_blogs')
@login_required
def my_blogs():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    posts = user.blogs
    return render_template('my_blogs.html', posts=posts)

@app.route('/update_blog/<int:blog_id>', methods=['GET', 'POST'])
@login_required
def update_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    if blog.author != current_user:
        abort(403)
    form = UpdateBlogForm()
    if form.validate_on_submit():
        blog.title = form.title.data
        blog.content = form.content.data
        db.session.commit()
        return redirect(url_for('my_blogs'))
    elif request.method == 'GET':
        form.title.data = blog.title
        form.content.data = blog.content
    return render_template('update_blog.html', form=form)

@app.route('/delete_blog/<int:blog_id>', methods=['POST'])
@login_required
def delete_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    if blog.author != current_user:
        abort(403)
    db.session.delete(blog)
    db.session.commit()
    return redirect(url_for('my_blogs'))

@app.route('/add_comment/<int:blog_id>', methods=['POST'])
@login_required
def add_comment(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, blog=blog, author=current_user)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('view_blog', blog_id=blog.id))
    return render_template('view_blog.html', blog=blog, form=form)

@app.route('/view_blog/<int:blog_id>')
def view_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    comments = blog.comments.order_by(Comment.timestamp.asc())
    form = CommentForm()
    return render_template('view_blog.html', blog=blog, form=form, comments=comments)


@app.route('/like/<int:blog_id>')
@login_required
def like(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    like = LikeDislike.query.filter_by(user_id=current_user.id, blog_id=blog.id).first()
    if like:
        if like.like:
            db.session.delete(like)
        else:
            like.like = True
            like.dislike = False
        db.session.commit()
    else:
        new_like = LikeDislike(user_id=current_user.id, blog_id=blog.id, like=True, dislike=False)
        db.session.add(new_like)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/dislike/<int:blog_id>')
@login_required
def dislike(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    dislike = LikeDislike.query.filter_by(user_id=current_user.id, blog_id=blog.id).first()
    if dislike:
        if dislike.dislike:
            db.session.delete(dislike)
        else:
            dislike.dislike = True
            dislike.like = False
        db.session.commit()
    else:
        new_dislike = LikeDislike(user_id=current_user.id, blog_id=blog.id, dislike=True, like=False)
        db.session.add(new_dislike)
        db.session.commit()
    return redirect(url_for('index'))
