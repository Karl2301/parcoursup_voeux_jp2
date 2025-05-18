"""
Fonctionnalité:
- La fonction `logout` gère la déconnexion de l'utilisateur en supprimant le cookie de session de l'utilisateur et en réinitialisant le cookie stocké dans la base de données.

Utilisation:
- Cette route est appelée lorsque l'utilisateur souhaite se déconnecter de l'application. Elle vérifie si un cookie de session est présent, et si oui, elle réinitialise le cookie associé à l'utilisateur dans la base de données et supprime le cookie de session du navigateur de l'utilisateur.

Modules importés:
- flask: Pour gérer les requêtes HTTP et les sessions.
- SQLClassSQL: Pour interagir avec la classe `Student`.
- ext_config: Pour obtenir l'application Flask et le moteur de base de données.
- werkzeug.security: Pour les fonctions de hachage de mot de passe.
- sqlmodel: Pour les sessions et les requêtes SQL.
- json, uuid: Pour la manipulation de données JSON et la génération d'identifiants uniques.
"""

from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
import uuid
from flask_socketio import SocketIO, emit, join_room, leave_room
from ds import send_discord_message

def logout():
    session_cookie = request.cookies.get('session_cookie')
    app.logger.info("Client IP: %s", get_client_ip())
    app.logger.info("Session cookie: %s", session_cookie)
    if session_cookie:
        with Session(engine) as session:
            user = get_user_by_cookie(session, session_cookie)
            if user:
                user.cookie = None
                user.online = False
                session.add(user)
                session.commit()
                send_discord_message("utilisateur_deconnecte", user.identifiant_unique, get_url_from_request(request), get_client_ip())

            professeurs = session.exec(select(Superieurs).where(Superieurs.professeur == True)).all()
            for professeur in professeurs:
                try:
                    if professeur.cookie:  # Vérifier que le professeur a un cookie de connexion valide
                        classes_professeur = json.loads(professeur.niveau_classe)
                        if user.niveau_classe in classes_professeur:
                            emit('online_student', {
                                'eleve_id': user.identifiant_unique,
                                'status': 'HORS LIGNE',
                            }, room=professeur.cookie, namespace='/')
                            app.logger.info(f"Notification statut hors ligne envoyée au professeur {professeur.identifiant_unique} pour l'élève {user.identifiant_unique}")
                except json.JSONDecodeError:
                    logging.error(f"Erreur de parsing JSON pour le professeur {professeur.identifiant_unique}")

    response = make_response(redirect(url_for('home')))
    response.set_cookie('session_cookie', '', expires=0)
    app.logger.info("User logged out successfully")
    return response