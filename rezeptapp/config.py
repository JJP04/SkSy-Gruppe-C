import os

class Config:
    SECRET_KEY = 'geheim123'
    INSTANCE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app', 'instance')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(INSTANCE_PATH, 'test.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

