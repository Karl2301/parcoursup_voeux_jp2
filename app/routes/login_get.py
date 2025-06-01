"""
Ce fichier définit la route pour la méthode GET de la page de connexion dans l'application Flask.
Fonctionnalité:
- Vérifie si un cookie de session est présent dans la requête.
- Si un cookie de session est trouvé, il tente de récupérer l'utilisateur correspondant dans la base de données.
- Si l'utilisateur est trouvé, il redirige vers le tableau de bord.
- Si aucun cookie de session n'est trouvé ou si l'utilisateur n'est pas trouvé, il affiche la page de connexion.
Utilisation:
- Ce fichier est utilisé lorsque l'utilisateur accède à la page de connexion de l'application.
"""

from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
from flask_socketio import SocketIO, emit, join_room, leave_room
import logging

def login_get():
    session_cookie = request.cookies.get('session_cookie')
    #app.logger.info("Client IP: %s", get_client_ip())
    #app.logger.info("Session cookie: %s", session_cookie)

    if session_cookie:
        with Session(engine) as session:
            user = get_user_by_cookie(session, session_cookie)
            if user:
                app.logger.info("User found: %s", user.identifiant_unique)
                if user.professeur == True and user.deja_connecte == False: # Si l'utilisateur est un professeur et n'a pas encore configuré son mot de passe
                    return redirect(url_for('configure_prof_get'))
                elif user.professeur == False and user.deja_connecte == False: # Si l'utilisateur est un élève et n'a pas encore configuré son mot de passe
                    return redirect(url_for('configure_password_get'))
                else:
                    app.logger.info("User found")
                    return redirect(url_for('dashboard'))
    
    app_config = get_app_config()
    is_in_maintenance = app_config.get('is_in_maintenance')
    maintenance_message = app_config.get('maintenance_message')
    maintenance_level = app_config.get('maintenance_level')

    return render_template('login/index.html', version=VERSION, public_key=PUBLIC_KEY, is_in_maintenance=is_in_maintenance, maintenance_message=maintenance_message, maintenance_level=maintenance_level)