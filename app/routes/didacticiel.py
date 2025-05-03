"""
Fichier: didacticiel.py
Ce fichier contient les routes et la logique associée à la gestion du didacticiel 
dans l'application Flask. Il gère les fonctionnalités suivantes :
1. Vérification de l'état du didacticiel pour un utilisateur :
    - La route `didacticiel_get` permet de vérifier si un utilisateur a complété 
      le didacticiel ou non. Elle renvoie une réponse JSON indiquant l'état 
      (`didacticielCompleted`).
2. Mise à jour de l'état du didacticiel :
    - La route `didacticiel_post` permet de marquer le didacticiel comme complété 
      pour un utilisateur. Une fois cette action effectuée, l'état est mis à jour 
      dans la base de données.
Ce fichier gère également les vérifications d'authentification via un cookie de session 
et redirige les utilisateurs non authentifiés vers la page de connexion. Il inclut des 
vérifications pour s'assurer que seuls les utilisateurs valides peuvent accéder ou 
mettre à jour l'état du didacticiel.
"""

from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
from flask_socketio import SocketIO, emit, join_room, leave_room
from ds import send_discord_message

def didacticiel_get():
    session_cookie = request.cookies.get('session_cookie')
    if not session_cookie:
        return redirect(url_for('login_get'))
    
    with Session(engine) as session:
        user = get_user_by_cookie(session, session_cookie)
        if not user:
            return redirect(url_for('login_get'))
        
        if user.admin or user.professeur:
            return jsonify({'didacticielCompleted': True})
        
        if user.didacticiel:
            return jsonify({'didacticielCompleted': True})
        else:
            return jsonify({'didacticielCompleted': False})

def didacticiel_post():
    session_cookie = request.cookies.get('session_cookie')
    if not session_cookie:
        return redirect(url_for('login_get'))
    
    with Session(engine) as session:
        user = get_user_by_cookie(session, session_cookie)
        if not user:
            return redirect(url_for('login_get'))
        
        if user.didacticiel:
            return redirect(jsonify({'ok': True}))
        
        user.didacticiel = True
        session.add(user)
        session.commit()
        send_discord_message("didacticiel_termine", user.identifiant_unique, get_url_from_request(request), get_client_ip())
        return jsonify({'ok': True})