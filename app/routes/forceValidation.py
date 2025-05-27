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


def force_validation():
    """
    data = request.get_json()  # Récupérer le contenu du POST en JSON
    identifiant = data.get('identifiant')
    """
    data = request.get_json()
    force = data.get('force')
    session_cookie = request.cookies.get('session_cookie')
    classe = data.get('classe')

    with Session(engine) as sessionuser:
        user = get_user_by_cookie(sessionuser, session_cookie)
        
        if not user:
            return jsonify({"error": "Utilisateur non trouvé."}), 404
        
        
        if user.professeur == False:
            return jsonify({"error": "Accès refusé. Seuls les professeurs peuvent forcer la validation."}), 403
        
        # Mettre à jour le statut de l'utilisateur
        with Session(engine) as sessionuser:
            users = sessionuser.exec(select(Users).where(Users.niveau_classe == classe)).all()
            if not users:
                return jsonify({"error": "Aucun utilisateur trouvé pour cette classe."}), 404
            
            for utilisateur in users:
                if not utilisateur.choix_validees:
                    app.logger.info(f"Utilisateur trouvé : {utilisateur.identifiant_unique}")
                    utilisateur.choix_validees = True
                    utilisateur.voeux_validation = datetime.now()
                    sessionuser.add(utilisateur)
            
            sessionuser.commit()

            # Vérifier si tous les utilisateurs ont validé leurs voeux
            all_users_validated = sessionuser.exec(select(Users).where(Users.choix_validees == False)).first() is None
            if all_users_validated:
                send_email_when_users_confirmed(sessionuser)
                send_discord_message("all_voeux_valides", "Tous les utilisateurs ont validé leurs voeux.", 'Serveur', "0.0.0.0")

            # Vérifier si tous les élèves de la classe de l'utilisateur ont validé leurs voeux
            all_class_users_validated = sessionuser.exec(select(Users).where(Users.niveau_classe == classe, Users.choix_validees == False)).first() is None
            if all_class_users_validated:
                send_email_to_prof_when_all_classe_validate(sessionuser, classe)
        
        return jsonify({"ok": True, "message": "Statut de l'utilisateur mis à jour avec succès."}), 200