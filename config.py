# config.py
import os

# Database connection settings
USERNAME = "root"  # Database login username
PASSWORD = "toor"  # Database login password
HOST = "localhost"  # Host of the MySQL server, typically 'localhost' or an IP address
PORT = "3308"  # Port number where MySQL is running (default is 3306, but it's 3308 here)
DATABASE = "ecc_enhance_db"  # Name of the database

# SQLAlchemy URI configuration
DB_URI = f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?charset=utf8'

# SQLAlchemy settings to let SQLAlchemy know how to connect to the database
SQLALCHEMY_DATABASE_URI = DB_URI

# Enables or disables Flask-SQLAlchemy's modification tracking
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Debugging and logging
# Log SQL queries for debugging purposes
SQLALCHEMY_ECHO = True


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'upload')
ALLOWED_EXTENSIONS = {'xlsx'}

