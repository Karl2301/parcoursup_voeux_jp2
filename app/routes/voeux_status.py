
"""
voeux_status.py
Ce fichier gère les routes liées au statut des voeux dans l'application Flask.
Il fournit des fonctionnalités pour récupérer et mettre à jour le statut des voeux
d'un utilisateur connecté via des cookies de session.
Fonctionnalités principales :
- `get_voeux_status`: Permet de récupérer le statut des choix validés pour un utilisateur.
- `post_voeux_status`: Permet de valider les choix d'un utilisateur après vérification des conditions.
Gestion :
- Vérifie la présence et la validité du cookie de session pour identifier l'utilisateur.
- Interagit avec la base de données via SQLModel pour récupérer et mettre à jour les informations utilisateur.
- Retourne des réponses JSON ou redirige vers la page de connexion en cas de problème d'authentification.
Ce fichier est essentiel pour gérer les interactions liées aux voeux des utilisateurs dans le cadre de l'application.
"""

from flask import Flask, request, redirect, url_for, jsonify
from sqlmodel import Session, select
from ext_config import *
import json
import logging
from ds import send_discord_message
from flask_socketio import emit, SocketIO

def get_voeux_status():
    session_cookie = request.cookies.get('session_cookie')
    if not session_cookie:
        return jsonify({'error': 'No session cookie'}), 400

    with Session(engine) as session:
        user = get_user_by_cookie(session, session_cookie)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({'choix_validees': user.choix_validees})

def post_voeux_status():
    session_cookie = request.cookies.get('session_cookie')
    if not session_cookie:
        return redirect(url_for('login_get'))

    data = request.get_json()
    choix_validees = data.get('validate')

    with Session(engine) as session:
        user = get_user_by_cookie(session, session_cookie)
        if user and not user.choix_validees:

            config = get_specific_config("disable_student_validate")
            if config and user.professeur == False and user.admin == False:
                return jsonify({'error': 'Validation des voeux bloquée pour les élèves.'}), 403

            voeux_etablissement = json.loads(user.voeux_etablissements)
            if all(voeu.get('enable') == False for voeu in voeux_etablissement):
                print('aucun choix fait')
                return jsonify({'error': 'aucun choix fait'}), 400
            
            user.choix_validees = True
            user.didacticiel = True
            user.voeux_validation = datetime.now()
            session.add(user)
            session.commit()
            send_discord_message("voeux_valides", user.identifiant_unique, get_url_from_request(request), get_client_ip())
            # Récupérer les professeurs ayant la classe de l'utilisateur dans leur liste et un cookie de connexion valide
            professeurs = session.exec(select(Superieurs).where(Superieurs.professeur == True)).all()
            for professeur in professeurs:
                try:
                    if professeur.cookie:  # Vérifier que le professeur a un cookie de connexion valide
                        classes_professeur = json.loads(professeur.niveau_classe)
                        if user.niveau_classe in classes_professeur:
                            emit('voeux_valides', {
                                'eleve_id': user.identifiant_unique,
                                'status': 'VALIDÉS'
                            }, room=professeur.cookie, namespace='/')
                            app.logger.info(f"Notification envoyée au professeur {professeur.identifiant_unique} pour l'élève {user.identifiant_unique}")
                except json.JSONDecodeError:
                    logging.error(f"Erreur de parsing JSON pour le professeur {professeur.identifiant_unique}")

            # Vérifier si tous les utilisateurs ont validé leurs voeux
            all_users_validated = session.exec(select(Users).where(Users.choix_validees == False)).first() is None
            if all_users_validated:
                send_email_when_users_confirmed(session)
                send_discord_message("all_voeux_valides", "Tous les utilisateurs ont validé leurs voeux.", 'Serveur', "0.0.0.0")

            # Vérifier si tous les élèves de la classe de l'utilisateur ont validé leurs voeux
            all_class_users_validated = session.exec(select(Users).where(Users.niveau_classe == user.niveau_classe, Users.choix_validees == False)).first() is None
            if all_class_users_validated:
                print(f"Tous les élèves de la classe {user.niveau_classe} ont validé leurs voeux")
                send_email_to_prof_when_all_classe_validate(session, user.niveau_classe)

            return {'status': True}
        else:
            return redirect(url_for('login_get'))