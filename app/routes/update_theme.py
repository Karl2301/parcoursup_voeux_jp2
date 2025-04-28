"""
Fichier: update_theme.py
Ce fichier contient les routes Flask permettant de gérer les préférences de thème 
du tableau de bord d'un utilisateur dans une application web. Il fournit deux 
fonctionnalités principales :
1. `update_theme` : Cette fonction permet de mettre à jour le thème (par exemple, 
    mode sombre ou clair) de l'utilisateur connecté. Elle récupère les données 
    envoyées via une requête POST en JSON, vérifie l'authenticité de l'utilisateur 
    à l'aide d'un cookie de session, et met à jour la préférence de thème dans la 
    base de données.
2. `get_theme` : Cette fonction permet de récupérer la préférence de thème actuelle 
    de l'utilisateur connecté. Elle vérifie l'authenticité de l'utilisateur à l'aide 
    d'un cookie de session et renvoie la préférence de thème sous forme de réponse JSON.
Ces routes nécessitent que l'utilisateur soit authentifié via un cookie de session 
valide. En cas d'absence ou d'invalidité du cookie, l'utilisateur est redirigé vers 
la page de connexion ou reçoit une réponse d'erreur appropriée.
"""

from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
from flask_socketio import SocketIO, emit, join_room, leave_room



def update_theme():
    session_cookie = request.cookies.get('session_cookie')
    data = request.get_json()  # Récupérer le contenu du POST en JSON
    darkTheme = data.get('darkTheme')
    if session_cookie:
        with Session(engine) as session:
            user = get_user_by_cookie(session, session_cookie)
            if user:
                user.dashboard_theme = darkTheme
                session.add(user)
                session.commit()
                return {'status': 'success'}
            else:
                return redirect(url_for('login_get'))
    else:
        return redirect(url_for('login_get'))
    

def get_theme():
    session_cookie = request.cookies.get('session_cookie')
    if session_cookie:
        with Session(engine) as session:
            user = get_user_by_cookie(session, session_cookie)
            if user:
                return jsonify({'darkTheme': user.dashboard_theme})
            else:
                return jsonify({'error': 'User not found'}), 404
    else:
        return jsonify({'error': 'No session cookie'}), 400