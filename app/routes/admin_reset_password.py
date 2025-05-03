from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
import uuid
from flask_socketio import SocketIO, emit, join_room, leave_room
from ds import send_discord_message

def admin_reset_password_post():
    session_cookie = request.cookies.get('session_cookie')
    app.logger.info("Client IP: %s", get_client_ip())
    app.logger.info("Session cookie: %s", session_cookie)

    # Vérifier si le cookie de session est présent
    if session_cookie is None:
        return redirect(url_for('login_get'))  
    
    with Session(engine) as session:
        adminuser = get_user_by_cookie(session, session_cookie)
        # Vérifier que l'utilisateur est bien un super admin (professeur et admin)
        if not adminuser:
            return redirect(url_for('login_get'))
        if not adminuser.admin:
            return redirect(url_for('dashboard'))
        if not adminuser.professeur:
            return redirect(url_for('dashboard'))
        
    
    # Récupérer le nom d'utilisateur du formulaire
    data = request.get_json()
    username = data.get('identifiant_unique')
    
    if not username:
        flash("Veuillez entrer un nom d'utilisateur.", "error")
        return jsonify({"ok": False, "message": "Utilisateur non trouvé."})
    
    with Session(engine) as session:
        # Vérifier si l'utilisateur existe
        statement = select(Superieurs).where(Superieurs.identifiant_unique == username)
        user = session.exec(statement).one_or_none()
        
        if not user:
            flash("Utilisateur non trouvé.", "error")
            return jsonify({"ok": False, "message": "Utilisateur non trouvé."})
        
        if user.professeur == False:
            flash("L'utilisateur est un élève, pas un professeur.", "error")
            return jsonify({"ok": False, "message": "L'utilisateur est un élève, pas un professeur."})
        if user.admin == True:
            flash("L'utilisateur est un administrateur.", "error")
            return jsonify({"ok": False, "message": "L'utilisateur est pas administrateur."})
    
        # Générer un nouveau mot de passe aléatoire
        new_password = "ProfMDP"
        user.password = generate_password_hash(new_password)
        user.deja_connecte = False
        user.online = False
        user.cookie = None
        session.add(user)
        session.commit()
        app.logger.info("Mot de passe réinitialisé pour l'utilisateur : %s", username)
        return jsonify({"ok": True, "message": "Utilisateur trouvé et réinitialisé."})
