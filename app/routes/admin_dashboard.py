"""
Ce fichier définit la route pour le tableau de bord (dashboard) de l'application Flask.
Fonctionnalité:
- La fonction `dashboard` gère la logique d'affichage du tableau de bord pour les utilisateurs authentifiés.
- Elle vérifie la présence d'un cookie de session et récupère l'utilisateur correspondant dans la base de données.
- Si l'utilisateur est trouvé, elle affiche la page du tableau de bord.
- Sinon, elle redirige l'utilisateur vers la page de connexion.
Utilisation:
- Ce fichier est utilisé lorsque l'utilisateur tente d'accéder à la route du tableau de bord.
"""

from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
from flask_socketio import SocketIO, emit, join_room, leave_room

def admin_dashboard():
    session_cookie = request.cookies.get('session_cookie')
    if session_cookie:
        with Session(engine) as session:
            user = get_user_by_cookie(session, session_cookie)
            if user:
                if user.professeur == True :
                    user_role="professeur"
                # elif user.admin == True:
                    # user_role="admin"
                else:   
                    user_role="eleve"
                
                if user.professeur == True and user.deja_connecte == False: # Si l'utilisateur est un professeur et n'a pas encore configuré son mot de passe
                    return redirect(url_for('configure_prof_get'))
                elif user.professeur == False and user.deja_connecte == False: # Si l'utilisateur est un élève et n'a pas encore configuré son mot de passe
                    return redirect(url_for('configure_password_get'))
                elif user.admin == True :
                    return render_template('admin_dashboard/index.html', user_role=user_role)
                else:
                    return render_template('dashboard/index.html', user_role=user_role)
    return redirect(url_for('login_get'))