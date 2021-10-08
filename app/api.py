import jwt
import datetime
from flask import request, jsonify
from app import app, db
from app.models import User, Post, post_schema, posts_schema, comment_schema, Comment, user_schema, comments_schema, \
    Album, albums_schema, ImageAlbum, image_album_schema, image_albums_schema
from werkzeug.security import generate_password_hash, check_password_hash
from app.authenticate import token_required
from flask_expects_json import expects_json
from .routes import save_img_post


schema_user = {
    'type': 'object',
    'properties': {
        'username': {'type': 'string'},
        'email': {'type': 'string'},
        'password': {'type': 'string'}
    },
    'required': ['username', 'email', 'password']
}

schema_post = {
    'type': 'object',
    'properties': {
        'title': {'type': 'string'},
        'content': {'type': 'string'}
    },
    'required': ['title', 'content']
}

schema_comment = {
    'type': 'object',
    'properties': {
        'comment': {'type': 'string'},
        'post_id': {'type': 'number'}
    },
    'required': ['comment', 'post_id']
}

schema_album = {
    'type': 'object',
    'properties': {
        'title': {'type': 'string'}
    },

}

schema_image = {
    'type': 'object',
    'properties': {
        'image': {'type': 'string'},
        'album_id': {'type': 'number'}
    },
    'required': ['image', 'album_id']
}


# USERS
@app.route('/api/user/register', methods=['POST'])
@expects_json(schema_user)
def create_user():
    data = request.get_json()

    qs_user = db.session.query(User.id).filter_by(username=data['username']).first() is not None

    if qs_user:
        return jsonify({'error': 'user already exists'}), 400

    password = generate_password_hash(data['password'])
    new_user = User(username=data['username'], email=data['email'], password_hash=password)
    db.session.add(new_user)
    db.session.commit()

    result = user_schema.dump(
        User.query.filter_by(username=data['username']).first()
    )

    return jsonify(result)


@app.route('/api/user/login', methods=['POST'])
def login_user():
    username = request.json['username']
    password = request.json['password']

    user = User.query.filter_by(username=username).first_or_404()

    payload = {
        'username': user.username,
        'exp': datetime.datetime.now() + datetime.timedelta(minutes=30)
    }

    if check_password_hash(user.password_hash, password):
        token = jwt.encode(payload, app.config['SECRET_KEY'])
        return jsonify({'token': token})

    return jsonify({'message': 'verify username and password'}), 401


# POSTS
@app.route('/api/post', methods=['POST'])
@token_required
@expects_json(schema_post)
def create_post(current_user):
    data = request.get_json()

    qs_post = db.session.query(Post.id).filter_by(title=data['title']).first() is not None

    if qs_post:
        return jsonify({'error': 'post already exists'}), 400

    new_post = Post(title=data['title'], content=data['content'], user_id=current_user.id, image=data['image'])

    db.session.add(new_post)
    db.session.commit()

    result = posts_schema.dump(
        Post.query.filter_by(user_id=current_user.id)
    )

    return jsonify(result)


@app.route('/api/posts', methods=['GET'])
def get_posts():
    result = posts_schema.dump(
        Post.query.all()
    )

    return jsonify(result)


@app.route('/api/post/<pk>', methods=['DELETE'])
@token_required
def delete_post(current_user, pk):
    post = Post.query.filter_by(id=pk).first_or_404()
    user_id = current_user.id

    if user_id != post.user_id:
        return jsonify({'error': 'unauthorized'})

    if not post:
        return jsonify({'message': 'post not found'}), 404

    db.session.delete(post)
    db.session.commit()

    return jsonify({'message': 'post removed successfully'})


# COMMENTS
@app.route('/api/comment', methods=['POST'])
@expects_json(schema_comment)
@token_required
def create_comment(current_user):
    data = request.get_json()

    new_comment = Comment(comment=data['comment'], user_id=current_user.id, post_id=data['post_id'])

    db.session.add(new_comment)
    db.session.commit()

    result = comments_schema.dump(
        Comment.query.filter_by(user_id=current_user.id)
    )

    return jsonify(result)


@app.route('/api/comment/<pk>', methods=['DELETE'])
@token_required
def delete_comment(current_user, pk):
    comment = Comment.query.filter_by(id=pk).first_or_404()
    user_id = current_user.id

    if user_id != comment.user_id:
        return jsonify({'error': 'unauthorized'})

    if not comment:
        return jsonify({'message': 'comment not found'})

    db.session.delete(comment)
    db.session.commit()

    return jsonify({'message': 'comment removed successfully'})


# ALBUMS
@app.route('/api/album', methods=['POST'])
@expects_json(schema_album)
@token_required
def create_album(current_user):
    data = request.get_json()

    new_album = Album(title=data['title'], user_id=current_user.id)

    db.session.add(new_album)
    db.session.commit()

    result = albums_schema.dump(
        Album.query.filter_by(user_id=current_user.id)
    )

    return jsonify(result)


@app.route('/api/album/<pk>', methods=['DELETE'])
@token_required
def delete_album(current_user, pk):
    album = Album.query.filter_by(id=pk).first()

    if not album:
        return jsonify({'message': 'album not found'})

    db.session.delete(album)
    db.session.commit()

    return jsonify({'message': 'album removed successfully'})


@app.route('/api/album/image/create', methods=['POST'])
@token_required
def image_create_teste(current_user):
    if request.method == "POST":
        data = request.form
        img = request.files

        image_file = save_img_post(img['image'])
        id_album = data['album_id']

        image_alb = ImageAlbum(image=image_file, album_id=id_album)

        db.session.add(image_alb)
        db.session.commit()

        result = image_albums_schema.dump(
            ImageAlbum.query.filter_by(album_id=data['album_id'])
        )

        return jsonify(result)


@app.route('/api/album/image/<pk>', methods=['DELETE'])
@token_required
def delete_image(current_user, pk):
    image = ImageAlbum.query.filter_by(id=pk).first()

    if not image:
        return jsonify({'message': 'album not found'})

    db.session.delete(image)
    db.session.commit()

    return jsonify({'message': 'image removed successfully'})
