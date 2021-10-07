import os
from werkzeug.utils import secure_filename
from app import app
from flask import render_template, flash, redirect, url_for, Response
from app.forms import LoginForm, RegistrationForm, PostForm, AlbumForm
from flask_login import current_user, login_user
from app.models import User, Post, Album
from flask_login import logout_user
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from app import db


@app.route('/')
@app.route('/index')
def index():
    posts = Post.query.limit(12).all()
    albuns = Album.query.limit(12).all()
    return render_template('index.html', title='index', posts=posts, albuns=albuns)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
def user(username):
    user_p = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(post_user=user_p)

    albuns = Album.query.filter_by(id=2).first()

    return render_template('user.html', user=user_p, posts=posts, albuns=albuns)


# POSTS
@app.route('/post/create', methods=['GET', 'POST'])
@login_required
def post_create():
    form = PostForm()
    id_user = current_user.id
    user_username = current_user.username
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, user_id=id_user)
        db.session.add(post)
        db.session.commit()
        flash('Congratulations, you are now a registered post!')
        return redirect(url_for('user', username=user_username))
    return render_template('create_post.html', title='Register Post', form=form)


@app.route('/post/<slug>', methods=['GET'])
def post_slug(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()

    return render_template('post.html', post=post)


@app.route('/post/delete/<slug>', methods=['GET'])
def post_delete(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    user_username = current_user.username

    db.session.delete(post)
    db.session.commit()

    return redirect(url_for('user', username=user_username))


UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Albums
@app.route('/album/create', methods=['GET', 'POST'])
@login_required
def album_create():
    usuario = current_user.username
    print(usuario)
    if request.method == "POST":
        if request.files:
            image = request.files['images']
            save_path = os.path.join(UPLOAD_FOLDER, secure_filename(image.filename))
            image.save(save_path)

            # image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))

            filename = secure_filename(image.filename)
            mimetype = image.mimetype

            print(f'{UPLOAD_FOLDER}/{filename}')

            img = Album(image=image.read(), name=filename, user_id=1, mimetype=mimetype)
            db.session.add(img)
            db.session.commit()

        return "upload successfully"

    return render_template('create_album.html', title='Register Album')


@app.route('/album/image/<int:id>')
def view_image(id):
    img = Album.query.filter_by(id=id).first()
    return Response(img.image, mimetype=img.mimetype)
