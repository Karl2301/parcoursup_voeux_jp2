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
            if not user:
                return jsonify({"error": "Utilisateur non trouvé."}), 404
            
            for user in users:
                app.logger.info(f"Utilisateur trouvé : {user.identifiant_unique}")

        sessionuser.add(user)
        sessionuser.commit()
        
        return jsonify({"ok": True, "message": "Statut de l'utilisateur mis à jour avec succès."}), 200