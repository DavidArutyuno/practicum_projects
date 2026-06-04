import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI', default='sqlite:///db.sqlite3')
    SECRET_KEY = os.getenv(
        'SECRET_KEY', default='SUP3R-S3CR3T-K3Y-F0R-MY-PR0J3C')
    DISK_TOKEN = os.getenv(
        'DISK_TOKEN', default='y0_nbfoiu3445tno35_fd09v854bn2_cs0e8hrb4k')
    FLASK_RUN_PORT = os.getenv('FLASK_RUN_PORT', default=5000)
    BASE_URL = os.getenv('BASE_URL', default='http://localhost')
    MAX_LENGTH = 16
