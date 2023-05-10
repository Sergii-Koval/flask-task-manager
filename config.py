import os

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

SECRET_KEY = 'a9e21b7f8d5beace6eb4ba87b3ecf0b2'
