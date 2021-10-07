import os
from app import app
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm, PostForm, AlbumForm
from flask_login import current_user, login_user
from app.models import User, Post, Album, Comment, ImageAlbum
from flask_login import logout_user
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from app import db


@app.route('/')
@app.route('/index')
def index():
    posts = Post.query.limit(12).all()
    albums = Album.query.limit(12).all()
    return render_template('index.html', posts=posts, albums=albums)


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
    return render_template('users/login.html', form=form)


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
        flash('Congratulations, successfully registered!')
        return redirect(url_for('login'))
    return render_template('users/register.html', form=form)


@app.route('/user/<username>')
def user(username):
    user_p = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(post_user=user_p)

    albums = Album.query.filter_by(album_user=user_p)

    return render_template('users/user.html', user=user_p, posts=posts, albums=albums)


# POSTS
def save_img_post(picture_file):
    picture_name = picture_file.filename
    picture_path = os.path.join(app.root_path, 'static/images', picture_name)
    picture_file.save(picture_path)
    return picture_name


@app.route('/post/create', methods=['GET', 'POST'])
@login_required
def post_create():
    form = PostForm()
    id_user = current_user.id
    user_username = current_user.username
    if form.validate_on_submit():
        image_file = save_img_post(form.image.data)

        post = Post(title=form.title.data, image=image_file, content=form.content.data, user_id=id_user)

        db.session.add(post)
        db.session.commit()
        flash('Congratulations, successfully registered!')
        return redirect(url_for('user', username=user_username))
    return render_template('posts/create_post.html', title='Register Post', form=form)


@app.route('/post/<slug>', methods=['GET'])
def post_slug(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    commts = Comment.query.filter_by(post_id=post.id)
    if post.image:
        image_url = url_for('static', filename='images/' + post.image)

        return render_template('posts/post.html', post=post, comments=commts, image_url=image_url)
    return render_template('posts/post.html', post=post, comments=commts)


@app.route('/post/delete/<slug>', methods=['GET'])
@login_required
def post_delete(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    user_username = current_user.username

    db.session.delete(post)
    db.session.commit()
    flash('Post removed successfully')
    return redirect(url_for('user', username=user_username))


# Albums
@app.route('/album/create', methods=['GET', 'POST'])
@login_required
def album_create():
    form = AlbumForm()
    id_user = current_user.id
    user_username = current_user.username
    if form.validate_on_submit():
        album = Album(title=form.title.data, user_id=id_user)

        db.session.add(album)
        db.session.commit()
        flash('Congratulations, successfully registered!')
        return redirect(url_for('user', username=user_username))
    return render_template('albums/create_album.html', title='Register Album', form=form)


@app.route('/album/<slug>', methods=['GET'])
def album_slug(slug):
    album = Album.query.filter_by(slug=slug).first_or_404()
    images = ImageAlbum.query.filter_by(album_id=album.id)

    list_images = []
    for i in images:
        image_url = url_for('static', filename='images/' + i.image)
        list_images.append(image_url)

    return render_template('albums/album.html', album=album, images=list_images)


@app.route('/album/delete/<slug>', methods=['GET'])
@login_required
def album_delete(slug):
    album = Album.query.filter_by(slug=slug).first_or_404()
    user_username = current_user.username

    db.session.delete(album)
    db.session.commit()
    flash('Album removed successfully')
    return redirect(url_for('user', username=user_username))


@app.route('/album/image/create', methods=['POST'])
@login_required
def image_create():
    if request.method == "POST":
        data = request.form
        img = request.files

        image_file = save_img_post(img['image'])
        id_album = data['id_album']

        image_alb = ImageAlbum(image=image_file, album_id=id_album)

        db.session.add(image_alb)
        db.session.commit()

        album = Album.query.filter_by(id=data['id_album']).first()

        flash('Congratulations, successfully registered!')
        return redirect(url_for('album_slug', slug=album.slug))


@app.route('/comment/create', methods=['POST'])
@login_required
def comment_create():
    if request.method == "POST":
        id_user = current_user.id
        user_username = current_user.username
        data = request.form

        comment = Comment(comment=data['comment_input'], post_id=data['post_comment'], user_id=id_user)
        db.session.add(comment)
        db.session.commit()
        flash('Congratulations, you are now a registered comment!')

        post = Post.query.filter_by(id=data['post_comment']).first()

        return redirect(url_for('post_slug', slug=post.slug))


@app.route('/comment/delete/<pk>', methods=['GET'])
@login_required
def comment_delete(pk):
    comment = Comment.query.filter_by(id=pk).first_or_404()
    user_username = current_user.username

    db.session.delete(comment)
    db.session.commit()
    flash('Comment removed successfully')

    return redirect(url_for('user', username=user_username))
