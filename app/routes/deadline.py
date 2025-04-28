from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
from flask_socketio import SocketIO, emit, join_room, leave_room
from .planification import planifier_execution
import logging

def deadline_post():
    session_cookie = request.cookies.get('session_cookie')
    app.logger.info("Client IP: %s", get_client_ip())
    app.logger.info("Session cookie: %s", session_cookie)

    if not session_cookie:
        return redirect(url_for('login_get'))
    
    with Session(engine) as session:
        user = get_user_by_cookie(session, session_cookie)
        # Vérifier que l'utilisateur est bien un super admin (professeur et admin)
        if not (user and user.professeur and user.admin):
            abort(403)  # Accès interdit
        
        data = request.get_json()
        deadline_str = data.get('deadline')
        app.logger.info("Deadline reçue : %s", deadline_str)
        try:
            # Convertir la date du format YYYY-MM-DDTHH:MM au format datetime
            new_deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M') if deadline_str else None
            if new_deadline:
                # Forcer l'heure à 23h59
                new_deadline = new_deadline.replace(hour=23, minute=59, second=0, microsecond=0)
        except ValueError:
            new_deadline = None  # Gestion d'erreur, éventuellement ajouter un message
        
        # Récupérer ou créer l'enregistrement de configuration
        config = session.exec(select(Config)).first()
        if config:
            config.deadline = new_deadline
        else:
            config = Config(deadline=new_deadline)
            session.add(config)
        session.commit()
        planifier_execution(new_deadline)
    app.logger.info("Deadline mise à jour avec succès")
    return jsonify(success=True)