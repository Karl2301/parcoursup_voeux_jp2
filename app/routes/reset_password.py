"""
Fichier: reset_password.py
Ce fichier gère les fonctionnalités liées à la réinitialisation des mots de passe 
dans l'application Flask. Il contient les routes et les fonctions nécessaires pour 
permettre aux utilisateurs autorisés (comme les professeurs) de réinitialiser les mots 
de passe des étudiants.
Fonctionnalités principales :
- Vérification des droits d'accès de l'utilisateur via un cookie de session.
- Validation des privilèges de l'utilisateur pour s'assurer qu'il est autorisé à effectuer 
    une réinitialisation de mot de passe.
- Réinitialisation du mot de passe d'un étudiant en générant un nouveau mot de passe par défaut.
- Gestion des erreurs et journalisation des actions pour assurer la traçabilité.
Ce fichier utilise les bibliothèques Flask, SQLModel, et Werkzeug pour gérer les requêtes, 
les interactions avec la base de données, et la sécurité des mots de passe.
"""

from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
from flask_socketio import SocketIO, emit, join_room, leave_room

def reset_student_password(identifiant):
    try:
        session_cookie = request.cookies.get('session_cookie')
        app.logger.info("Client IP: %s", get_client_ip())
        app.logger.info("Password reset request by user: %s", session_cookie)
        if not session_cookie:
            return jsonify({'error': 'Vous devez être connecté pour réinitialiser un mot de passe'}), 403
        
        with Session(engine) as session:
            user = get_user_by_cookie(session, session_cookie)
            if not user:
                return jsonify({'error': 'Utilisateur non trouvé'}), 404

            if not user.professeur:
                return jsonify({'error': 'Vous n\'avez pas les droits pour réinitialiser un mot de passe'}), 403

        with Session(engine) as session:
            # Utilisation directe de l'identifiant pour la requête
            statement = select(Users).where(Users.identifiant_unique == identifiant)
            user = session.exec(statement).first()
            
            if user:
                # Forcer la réinitialisation du mot de passe
                user.deja_connecte = False
                user.password = generate_password_hash("EleveMDP")
                session.add(user)
                session.commit()
                app.logger.info("Password reset successfully for student: %s", identifiant)
                return jsonify({'success': True, 'message': 'Mot de passe réinitialisé avec succès'}), 200
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500