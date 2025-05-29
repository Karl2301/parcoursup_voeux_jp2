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
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Random import get_random_bytes
from Crypto import Random


def login_post():
    """
    data = request.get_json()  # Récupérer le contenu du POST en JSON
    identifiant = data.get('identifiant')
    """

    data = request.get_json()
    encrypted_username = data['username']
    encrypted_password = data['password']

    # Déchiffrement
    private_key = RSA.import_key(PRIVATE_KEY)  # PRIVATE_KEY est une chaîne de caractères contenant la clé privée au format PEM
    cipher = PKCS1_v1_5.new(private_key)

    # Déchiffrement
    sentinel = Random.new().read(15)  # Valeur de secours pour le déchiffrement
    try:
        identifiant = cipher.decrypt(base64.b64decode(encrypted_username), sentinel).decode()
        password = cipher.decrypt(base64.b64decode(encrypted_password), sentinel).decode()
    except ValueError:
        app.logger.error("Erreur de déchiffrement pour l'identifiant ou le mot de passe.")
        return jsonify({"error": "Nom d'utilisateur ou mot de passe incorrect."})

    app.logger.info("Client IP: %s", get_client_ip())
    app.logger.info("Login attempt for user: %s", identifiant)

    with Session(engine) as sessionuser:
        user = get_user_by_identifiant(sessionuser, identifiant)
        
        if not user:
            return jsonify({"error": "Nom d'utilisateur ou mot de passe incorrect."})
        
        config = get_specific_config("disable_student_access")
        if config and user.professeur == False and user.admin == False:
            return jsonify({"error": "Espace bloqué pour les élèves."})
        
        config = get_specific_config("disable_prof_access")
        if config and user.professeur == True and user.admin == False:
            return jsonify({"error": "Espace bloqué pour les professeurs."})
            
        if check_password_hash(user.password, password):
            new_session_cookie = str(uuid.uuid4())
            user.cookie = new_session_cookie
            user.online = True
            sessionuser.add(user)
            sessionuser.commit()

            professeurs = sessionuser.exec(select(Superieurs).where(Superieurs.professeur == True)).all()
            for professeur in professeurs:
                try:
                    if professeur.online:
                        classes_professeur = json.loads(professeur.niveau_classe)
                        if user.niveau_classe in classes_professeur:
                            emit('online_student', {
                                'eleve_id': user.identifiant_unique,
                                'status': 'EN LIGNE'
                            }, room=professeur.cookie, namespace='/')
                            app.logger.info(f"Notification statut en ligne envoyée au professeur {professeur.identifiant_unique} pour l'élève {user.identifiant_unique}")
                except json.JSONDecodeError:
                    logging.error(f"Erreur de parsing JSON pour le professeur {professeur.identifiant_unique}")
            
            # Redirections côté client
            if user.professeur == True and user.deja_connecte == False:
                return jsonify({
                    "redirect": url_for('configure_prof_get'),
                    "set_cookie": new_session_cookie
                })
            elif user.professeur == False and user.deja_connecte == False:
                return jsonify({
                    "redirect": url_for('configure_password_get'),
                    "set_cookie": new_session_cookie
                })
            else:
                app.logger.info("User logged in successfully: %s", user.identifiant_unique)
                send_discord_message("login_success", user.identifiant_unique, get_url_from_request(request))
                return jsonify({
                    "redirect": url_for('dashboard'),
                    "set_cookie": new_session_cookie
                })
        else:
            return jsonify({"error": "Nom d'utilisateur ou mot de passe incorrect."})