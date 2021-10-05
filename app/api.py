import jwt
import datetime
from flask import request, jsonify, make_response
from app import app, db
from app.models import User, Post
from werkzeug.security import generate_password_hash, check_password_hash


@app.route('/user/register', methods=['POST'])
def create_user():
    data = request.get_json()
    password = generate_password_hash(data['password'])
    new_user = User(username=data['username'], email=data['email'], password_hash=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'user created successfully'})


@app.route('/user/login', methods=['POST'])
def login_user():
    username = request.json['username']
    password = request.json['password']

    user = User.query.filter_by(username=username).first_or_404()

    payload = {
        'user': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }

    if check_password_hash(user.password_hash, password):
        token = jwt.encode(payload, app.config['SECRET_KEY'])
        return jsonify({'token': token})

    return jsonify({'message': 'verify username and password'}), 401

#
# @app.route('post/<slug>', methods=['DELETE'])
# def delete_post(slug):
#     post = Post.query.filter_by(slug=slug).first()
#
#     if not post:
#         return jsonify({'message': 'post not found'})
#
#     db.session.delete(post)
#     db.session.commit()
#
#     return jsonify({'message': 'post removed successfully'})
