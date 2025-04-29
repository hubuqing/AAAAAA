import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # GENIEACS 配置
    GENIEACS_URL = os.environ.get('GENIEACS_URL') or 'http://localhost:7557'
    GENIEACS_USERNAME = os.environ.get('GENIEACS_USERNAME') or 'admin'
    GENIEACS_PASSWORD = os.environ.get('GENIEACS_PASSWORD') or 'admin' 