import jwt
import datetime
from flask import request, jsonify
from app import app, db
from app.models import User, Post, post_schema, posts_schema, comment_schema, Comment, user_schema, comments_schema, \
    Album, albums_schema
from werkzeug.security import generate_password_hash, check_password_hash
from app.authenticate import token_required
from flask_expects_json import expects_json

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
        'content': {'type': 'string'},
        'user_id': {'type': 'number'}
    },
    'required': ['title', 'content', 'user_id']
}

schema_comment = {
    'type': 'object',
    'properties': {
        'comment': {'type': 'string'},
        'post_id': {'type': 'number'},
        'user_id': {'type': 'number'}
    },
    'required': ['comment', 'post_id', 'user_id']
}

schema_album = {
    'type': 'object',
    'properties': {
        'image': {'type': 'string'},
        'user_id': {'type': 'number'}
    },
    'required': ['user_id']
}


# USERS
@app.route('/api/user/register', methods=['POST'])
@expects_json(schema_user)
# @token_required
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
    print(current_user.username)

    qs_post = db.session.query(Post.id).filter_by(title=data['title']).first() is not None

    if qs_post:
        return jsonify({'error': 'post already exists'}), 400

    new_post = Post(title=data['title'], content=data['content'], user_id=data['user_id'])

    db.session.add(new_post)
    db.session.commit()

    result = posts_schema.dump(
        Post.query.filter_by(user_id=data['user_id'])
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
    post = Post.query.filter_by(id=pk).first()
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
def create_comment():
    data = request.get_json()

    new_comment = Comment(comment=data['comment'], user_id=data['user_id'], post_id=data['post_id'])

    db.session.add(new_comment)
    db.session.commit()

    result = comments_schema.dump(
        Comment.query.filter_by(user_id=data['user_id'])
    )

    return jsonify(result)


@app.route('/api/comment/<pk>', methods=['DELETE'])
@token_required
def delete_comment(current_user, pk):
    comment = Comment.query.filter_by(id=pk).first()
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
def create_album():
    data = request.get_json()

    new_album = Album(image=data['image'], user_id=data['user_id'])

    db.session.add(new_album)
    db.session.commit()

    result = albums_schema.dump(
        Comment.query.filter_by(user_id=data['user_id'])
    )

    return jsonify(result)


@app.route('/api/album/<pk>', methods=['DELETE'])
def delete_album(pk):
    album = Comment.query.filter_by(id=pk).first()

    if not album:
        return jsonify({'message': 'album not found'})

    db.session.delete(album)
    db.session.commit()

    return jsonify({'message': 'album removed successfully'})
