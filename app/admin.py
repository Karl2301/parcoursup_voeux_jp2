from flask import Flask, request, jsonify, render_template
from sqlmodel import SQLModel, create_engine, Session, Field
from typing import Optional
import pandas as pd
import os
from SQLClassSQL import *
from flask_socketio import SocketIO, emit, join_room, leave_room
from fonctions import *
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.orm import sessionmaker, scoped_session
from ext_config import app, engine


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Utilisation de scoped_session pour éviter les erreurs de contexte
session = scoped_session(SessionLocal)

# Initialisation de Flask-Admin
admin = Admin(app, name="Voeux-JP2 Admin Panel", template_mode="bootstrap3")

# Ajout des modèles à Flask-Admin avec la session
admin.add_view(ModelView(Users, session, name="Utilisateurs"))
admin.add_view(ModelView(Superieurs, session, name="Supérieurs"))
admin.add_view(ModelView(IdentifiantPerdus, session, name="Identifiants Perdus"))
admin.add_view(ModelView(DemandeAide, session, name="Demandes Aide"))
admin.add_view(ModelView(Classes, session, name="Classes"))
admin.add_view(ModelView(NotificationsVoeux, session, name="Notifications Voeux"))

# Fermer la session après chaque requête pour éviter les fuites mémoire
@app.teardown_appcontext
def remove_session(exception=None):
    session.remove()