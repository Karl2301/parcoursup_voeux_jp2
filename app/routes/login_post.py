"""
Ce fichier contient la route pour la gestion de la connexion des utilisateurs dans l'application Flask.
Fonctionnalité principale:
- `login_post`: Cette fonction est appelée lorsqu'un utilisateur soumet le formulaire de connexion. Elle vérifie l'identifiant de l'utilisateur dans la base de données, génère un cookie de session unique, met à jour la base de données avec ce cookie, et le définit dans le navigateur de l'utilisateur.
Utilisation:
- Ce fichier est utilisé lorsque l'utilisateur tente de se connecter à l'application via le formulaire de connexion. Si l'identifiant est trouvé dans la base de données, l'utilisateur est redirigé vers la page d'accueil avec un cookie de session. Sinon, rien ne se passe.
"""

from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
import uuid
from flask_socketio import SocketIO, emit, join_room, leave_room
from ds import send_discord_message
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

def login_post():
    """
    data = request.get_json()  # Récupérer le contenu du POST en JSON
    identifiant = data.get('identifiant')
    """

    identifiant = request.form['identifiant']
    password = request.form['password']
    ip_address = get_client_ip()





    
    app.logger.info("Client IP: %s", get_client_ip())
    app.logger.info("Login attempt for user: %s", identifiant)

    with Session(engine) as sessionuser:
        user = get_user_by_identifiant(sessionuser, identifiant)
        
        if not user:
            return render_template("login/index.html", error="Nom d'utilisateur ou mot de passe incorrect.")
        
        config = get_specific_config("disable_student_access")
        if config and user.professeur == False and user.admin == False: # Si l'accès élève est désactivé
            return render_template("login/index.html", error="Espace bloqué pour les élèves.")
        
        config = get_specific_config("disable_prof_access")
        if config and user.professeur == True and user.admin == False: # Si l'accès professeur est désactivé
            return render_template("login/index.html", error="Espace bloqué pour les professeurs.")
            
        if check_password_hash(user.password, password):
            # Générer un nouveau cookie de session
            new_session_cookie = str(uuid.uuid4())

            user.cookie = new_session_cookie
            user.online = True  # Mettre l'utilisateur en ligne
            
            sessionuser.add(user)
            sessionuser.commit()

            professeurs = sessionuser.exec(select(Superieurs).where(Superieurs.professeur == True)).all()
            for professeur in professeurs:
                try:
                    if professeur.cookie:  # Vérifier que le professeur a un cookie de connexion valide
                        classes_professeur = json.loads(professeur.niveau_classe)
                        if user.niveau_classe in classes_professeur:
                            emit('online_student', {
                                'eleve_id': user.identifiant_unique,
                                'status': 'EN LIGNE'
                            }, room=professeur.cookie, namespace='/')
                            app.logger.info(f"Notification statut en ligne envoyée au professeur {professeur.identifiant_unique} pour l'élève {user.identifiant_unique}")
                except json.JSONDecodeError:
                    logging.error(f"Erreur de parsing JSON pour le professeur {professeur.identifiant_unique}")
               
            if user.professeur == True and user.deja_connecte == False: # Si l'utilisateur est un professeur et n'a pas encore configuré son mot de passe
                response = make_response(redirect(url_for('configure_prof_get')))
                response.set_cookie('session_cookie', new_session_cookie, samesite='Lax')
            elif user.professeur == False and user.deja_connecte == False: # Si l'utilisateur est un élève et n'a pas encore configuré son mot de passe
                response = make_response(redirect(url_for('configure_password_get')))
                response.set_cookie('session_cookie', new_session_cookie, samesite='Lax')
            else:
                app.logger.info("User logged in successfully: %s", user.identifiant_unique)
                send_discord_message("login_success", user.identifiant_unique, get_url_from_request(request))
                response = make_response(redirect(url_for('dashboard')))
                response.set_cookie('session_cookie', new_session_cookie, samesite='Lax')
            return response
        else:
            error_message = "Nom d'utilisateur ou mot de passe incorrect."
            return render_template('login/index.html', error=error_message)
