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
from flask_turnstile import Turnstile
import time

def update_application_on_server():
    """
    Met à jour l'application sur le serveur.
    """
    app.logger.info(f"Chemin: {os.popen('pwd').read().strip()}")

app = Flask(__name__)
app.secret_key = os.urandom(24) 
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # 30 jours en secondes
app.config['TURNSTILE_SITE_KEY'] = os.getenv('TURNSTILE_SITE_KEY')
app.config['TURNSTILE_SECRET_KEY'] = os.getenv('TURNSTILE_SECRET_KEY')
app.config['TURNSTILE_ENABLED'] = True  # Optionnel, True par défaut

turnstile = Turnstile(app=app)
socketio = SocketIO(app, async_mode="eventlet") 

CORS(app)
# Configuration de la base de données MariaDBDA
DATABASE_USER = os.getenv('MYSQL_USER')
DATABASE_PASSWORD = os.getenv('MYSQL_PASSWORD')
DATABASE_URL = "mysql+pymysql://{}:{}@localhost/jp2_voeux_parcoursup".format(DATABASE_USER, DATABASE_PASSWORD)
# DATABASE_URL = "mysql+pymysql://nsidb:123nsi!bd@localhost/jp2_voeux_parcoursup"
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
update_application_on_server()


