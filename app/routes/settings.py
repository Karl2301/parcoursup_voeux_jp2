"""
FICHIER: settings.py
DESCRIPTION:
Ce fichier gère les routes et les fonctionnalités liées aux paramètres utilisateur dans l'application Flask.
Il permet de gérer les préférences de l'utilisateur, telles que le thème du tableau de bord, et de fournir
des réponses JSON ou des redirections en fonction de l'état de la session utilisateur.
FONCTIONNALITÉS:
- Vérification de la session utilisateur via un cookie de session.
- Récupération des informations utilisateur à partir de la base de données.
- Rendu de la page des paramètres utilisateur avec les préférences personnalisées.
- Fourniture d'une API pour récupérer le thème du tableau de bord de l'utilisateur au format JSON.
- Gestion des redirections vers la page de connexion si l'utilisateur n'est pas authentifié.
UTILISATION:
Ce fichier est utilisé pour centraliser la logique des paramètres utilisateur et fournir des routes
accessibles via l'interface web ou des appels API.
"""

from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
from flask_socketio import SocketIO, emit, join_room, leave_room


def settings():
    session_cookie = request.cookies.get('session_cookie')
    if session_cookie:
        with Session(engine) as session:
            user = get_user_by_cookie(session, session_cookie)
            if user:
                return render_template('settings/settings.html', dashboard_theme=user.dashboard_theme)
            else:
                return redirect(url_for('login_get'))

    else:
        return redirect(url_for('login_get'))
    

    

def settings_get_theme():
    session_cookie = request.cookies.get('session_cookie')
    if session_cookie:
        with Session(engine) as session:
            user = get_user_by_cookie(session, session_cookie)
            if user:
                return jsonify({'darkTheme': user.dashboard_theme})
            else:
                return jsonify({'error': 'User not found'}), 404

    else:
        return redirect(url_for('login_get'))