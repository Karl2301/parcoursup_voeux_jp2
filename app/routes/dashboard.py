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

def dashboard():
    session_cookie = request.cookies.get('session_cookie')
    if session_cookie:
        with Session(engine) as session:
            user = get_user_by_cookie(session, session_cookie)
            if user:
                # Récupérer la configuration contenant la deadline
                config = session.exec(select(Config)).first()
                deadline = config.deadline if config else None

                user_role = "Administrateur" if user.professeur == True and user.admin == True else "Professeur" if user.professeur == True else "Élève"
                if user.professeur == True and user.deja_connecte == False:  # Professeur qui n'a pas configuré son mot de passe
                    return redirect(url_for('configure_prof_get'))
                elif user.professeur == False and user.deja_connecte == False:  # Élève qui n'a pas configuré son mot de passe
                    return redirect(url_for('configure_password_get'))
                else:
                    if user.professeur == True:
                        if user.admin == True:
                            return render_template('dashboard_super_administrateur/index.html', user_role=user_role, deadline=deadline)
                        
                        return render_template('dashboard_prof/index.html', user_role=user_role, deadline=deadline)
                    else:
                        return render_template('dashboard_eleve/index.html', user_role=user_role, deadline=deadline)
    return redirect(url_for('login_get'))