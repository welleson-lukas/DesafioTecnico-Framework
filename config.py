import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'desafio-python-framework'
    JSON_SORT_KEYS = True
    DEBUG = True
    #UPLOADED_IMAGE_DEST = 'app/static/images'
    # UPLOADED_IMAGE_DEST = os.path.join(basedir, 'app/static/images')
    UPLOAD_FOLDER = 'app/static/images'
