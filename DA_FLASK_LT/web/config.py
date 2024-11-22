import os
class Config:
    SECRET_KEY = os.urandom(24)
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = '123456'