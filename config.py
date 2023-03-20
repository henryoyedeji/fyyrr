import os


class Config(object):
    SECRET_KEY = os.urandom(32)
    # Grabs the folder where the script runs.
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Enable debug mode.
    os.environ['FLASK_DEBUG'] = 'False'

    # Connect to the database

    # TODO IMPLEMENT DATABASE URL
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:Overflow@localhost:5432/fyyrr'
