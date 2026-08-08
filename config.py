import os

BASE_DIR = os.path.dirname(__file__)

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(
    os.path.join(BASE_DIR, 'ajiteu.db')
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'dev'
JWT_SECRET_KEY = 'jwt-dev-secret'
JWT_EXPIRE_HOURS = 24