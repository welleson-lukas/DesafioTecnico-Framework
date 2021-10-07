from datetime import datetime
from sqlalchemy import event
from app import db, ma
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from slugify import slugify


# USERS
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='post_user', lazy='dynamic')
    comments = db.relationship('Comment', backref='comment_user', lazy='dynamic')
    albuns = db.relationship('Album', backref='album_user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, username, email, password_hash):
        self.username = username
        self.email = email
        self.password_hash = password_hash


# POSTS
class Post(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(140))
    slug = db.Column(db.String(255), unique=True, nullable=True)
    content = db.Column(db.Text)
    created_on = db.Column(db.DateTime, index=True, default=datetime.now, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    comments = db.relationship('Comment', backref='comments', lazy='dynamic')

    def __repr__(self):
        return '<Post {}>'.format(self.title)

    def __init__(self, title, content, user_id):
        self.title = title
        self.content = content
        self.user_id = user_id

    @staticmethod
    def slugify(target, value, oldvalue, initiator):
        if value and (not target.slug or value != oldvalue):
            target.slug = slugify(value)


event.listen(Post.title, 'set', Post.slugify, retval=False)


# COMMENTS
class Comment(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    comment = db.Column(db.Text)
    created_on = db.Column(db.DateTime, index=True, default=datetime.now, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __repr__(self):
        return '<Comment {}>'.format(self.user_id)

    def __init__(self, comment, user_id, post_id):
        self.comment = comment
        self.user_id = user_id
        self.post_id = post_id


# Album
class Album(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    image = db.Column(db.String(255))
    name = db.Column(db.String(255))
    mimetype = db.Column(db.String(100))
    created_on = db.Column(db.DateTime, index=True, default=datetime.now, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Album {}>'.format(self.user_id)

    def __init__(self, image, name, mimetype, user_id):
        self.image = image
        self.name = name
        self.mimetype = mimetype
        self.user_id = user_id


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'email')


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class CommentSchema(ma.Schema):
    class Meta:
        fields = ('id', 'comment', 'user_id', 'post_id')


comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)


class PostSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'content', 'slug', 'created_on', 'updated_on', 'user_id', 'comments')

    comments = ma.Nested(CommentSchema, many=True)


post_schema = PostSchema()
posts_schema = PostSchema(many=True)


class AlbumSchema(ma.Schema):
    class Meta:
        fields = ('id', 'image', 'name', 'user_id', 'created_on', 'mimetype')


album_schema = AlbumSchema()
albums_schema = AlbumSchema(many=True)
