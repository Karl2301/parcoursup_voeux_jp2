from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from sqlmodel import SQLModel, create_engine, Session, Field
from sqlalchemy import text
from typing import Optional
import pandas as pd
import os
from SQLClassSQL import *
from flask_socketio import SocketIO, emit, join_room, leave_room
from fonctions import *
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.orm import sessionmaker, scoped_session
import logging
from logging.handlers import RotatingFileHandler
import asyncio
import json
import time
from dotenv import load_dotenv
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64

VERSION = "4.0.0"
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

def update_application_on_server():
    """
    Met à jour l'application sur le serveur.
    """
    app.logger.info(f"Chemin: {os.popen('pwd').read().strip()}")

app = Flask(__name__)
app.secret_key = os.urandom(24) 
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # 30 jours en 

socketio = SocketIO(app, async_mode="eventlet") 

CORS(app)
# Configuration de la base de données MariaDBDA
app_config = get_app_config()
is_in_maintenance = app_config.get('is_in_maintenance')

DATABASE_USER = os.getenv('MYSQL_USER')
DATABASE_PASSWORD = os.getenv('MYSQL_PASSWORD')
MARIADB_PORT = os.getenv('MARIADB_PORT')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
APP_PORT = os.getenv('APP_PORT')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD', "")
maintenance_mode = is_in_maintenance

if not APP_PORT:
    raise ValueError("La variable d'environnement APP_PORT doit être définie.")

if not DATABASE_USER or not DATABASE_PASSWORD or not MARIADB_PORT:
    raise ValueError("Les variables d'environnement MYSQL_USER, MYSQL_PASSWORD et MARIADB_PORT doivent être définies.")

DATABASE_URL = f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@localhost:{MARIADB_PORT}/{MYSQL_DATABASE}"
# DATABASE_URL = "sqlite:///database.sqlite3"

def create_engine_with_retries(database_url, retries=15, delay=5):
    for attempt in range(retries):
        try:
            engine = create_engine(
                database_url,
                pool_pre_ping=True,
                pool_recycle=280,
                pool_size=10,
                max_overflow=5,
            )
            with engine.connect() as connection:
                connection.execute(text("SHOW DATABASES;"))  # ← Fix ici
            return engine
        except Exception as e:
            app.logger.error(f"Database connection failed on attempt {attempt + 1}/{retries}: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                app.logger.error("All retries for database connection have failed.")
                return None


engine = create_engine_with_retries(DATABASE_URL)

SQLModel.metadata.create_all(engine)

try:
    public_key_path = os.path.join(os.path.dirname(__file__), 'public.pem')
    with open(public_key_path, 'r') as public_key_file:
        PUBLIC_KEY = public_key_file.read()
except FileNotFoundError:
    app.logger.error("Public key file not found.")
    abort(500, description="Public key file is missing.")

try:
    private_key_path = os.path.join(os.path.dirname(__file__), 'private.pem')
    with open(private_key_path, 'r') as private_key_file:
        PRIVATE_KEY = private_key_file.read()
except FileNotFoundError:
    app.logger.error("Private key file not found.")
    abort(500, description="Private key file is missing.")

if not os.path.exists('logs'):
    os.mkdir('logs')

file_handler = RotatingFileHandler('logs/app.log', maxBytes=10 * 1024 * 1024, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

app.logger.setLevel(logging.INFO)
app.logger.info('Application startup')
app.logger.info('Database connection established')
app.logger.info('Logging system initialized')
app.logger.info('Verification de l\'existence du fichier de configuration...')

config_path=os.path.join(os.path.dirname(__file__), 'config.json')
print(config_path)
print(os.path.exists(config_path))
if not os.path.exists(config_path):
    app.logger.info('Fichier de configuration introuvable, création d\'un nouveau fichier.')
    with open(config_path, 'w') as config_file:
        config_data = {
            "disable_student_access": False,
            "disable_prof_access": False,
            "disable_prof_reset_voeux": False,
            "disable_student_validate": False,
            "is_in_maintenance": False,
            'maintenance_message': ""
        }
        json.dump(config_data, config_file, indent=4)
        app.logger.info('Fichier de configuration créé avec succès.')
update_application_on_server()


# Message chiffré (remplacez par votre message chiffré en Base64)
encrypted_message = "JyfrUJIuLU8x1dDvbugohaGif9BOE3sqlVC9KwIel/EAhSede3R6I226HdX0QY82BN2hdKnXlbRjdkdHN79dJLrfocWfZil6qk0wB/TIXakzvQSZAE9noqyr0YLmvEp0sf/UPZzGDx2py9Tya0mmTDP7RcyP8bYZK+BKAdTvpfaN+Nt/KHNy6d/oTAFneRX2S80Uga+lYX821Bb33SSy3l49i87EMt1Zq9QksBAQq01l2w7E7vhUdWdZ0qz4HZQ4Lj/SMZxfUUACUXJVU3PCSGkvP+uc5/9EKv9OzfI92L4k6tM6wzD91fHl1jhiIh/a6Tz7pK+n95NIdaWNM+om+A==/J3YKxX77wvhzZ1CwrcnmxH94IBhBwcRuyCzVpALdbRI5XJjKOtTV4rCbi5HUtqcl3u54UJ20KabatMz44D3d+DTgU+OXjL0OvIT1pEYyvgKUdlxNMTtzzuPC0SwTGblALlLUyrrSIrFp5cYC/DYsdcok68gtdP4CwqhWiGHzZfHPQZzKHAKYpgXw=="

# Déchiffrement
def decrypt_message(encrypted_data, private_key):
    private_key = RSA.import_key(private_key)
    cipher = PKCS1_OAEP.new(private_key)
    decrypted_data = cipher.decrypt(base64.b64decode(encrypted_data))
    return decrypted_data.decode("utf-8")

# Test
try:
    decrypted_message = decrypt_message(encrypted_message, PRIVATE_KEY)
    print("Message déchiffré :", decrypted_message)
except Exception as e:
    print("Erreur lors du déchiffrement :", str(e))

