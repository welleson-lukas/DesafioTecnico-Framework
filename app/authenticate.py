import jwt
from functools import wraps
from app import app, db
from flask import request, jsonify, current_app
from app.models import User


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'authorization' in request.headers:
            token = request.headers['authorization']

        if not token:
            return jsonify({'error': 'unauthorized'}), 403

        if not "Bearer" in token:
            return jsonify({'error': 'invalid token'}), 401

        try:
            token_pure = token.replace("Bearer", "")
            decoded = jwt.decode(token_pure, app.config['SECRET_KEY'], algorithms="HS256",
                                 options={"verify_signature": False})
            current_user = User.query.filter_by(username=decoded['username']).first()

        except:
            return jsonify({'error': 'invalid token'}), 403

        return f(current_user, *args, **kwargs)

    return decorated
