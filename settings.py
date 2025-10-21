import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SECRET_KEY = os.getenv('SECRET_KEY')
    DISK_TOKEN = os.getenv('DISK_TOKEN')
    FLASK_RUN_PORT = os.getenv('FLASK_RUN_PORT')
    SERVER_NAME = 'localhost'
    PREFERRED_URL_SCHEME = 'http'
