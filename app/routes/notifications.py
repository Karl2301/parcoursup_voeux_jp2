"""
notifications.py
Ce fichier gère les fonctionnalités liées aux notifications dans l'application Flask.
Il permet de récupérer et d'afficher les demandes d'aide et les notifications de vœux
associées aux classes d'un professeur connecté. Les fonctionnalités principales incluent :
- Définir un filtre Jinja pour formater les dates dans les templates HTML.
- Récupérer les notifications et demandes d'aide en fonction des classes d'un professeur.
- Vérifier l'authentification de l'utilisateur via un cookie de session.
- Rediriger les utilisateurs non autorisés ou non authentifiés vers les pages appropriées.
Ce fichier est essentiel pour afficher les notifications pertinentes aux utilisateurs
ayant des droits de professeur dans l'application.
"""

from flask import Flask, render_template
from datetime import datetime
from sqlmodel import Session, select
from ext_config import *

def format_datetime(value):
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime("%d/%m %H:%M")
    except Exception:
        return value

# Enregistrer le filtre dans l'environnement Jinja de l'app
app.jinja_env.filters['formatdatetime'] = format_datetime

def get_notifications():
    """
    Récupère toutes les demandes d'aide en affichant l'id, le titre, le message et la classe.
    """
    session_cookie = request.cookies.get('session_cookie')

    if not session_cookie:
        return redirect(url_for('login_get'))
    
    with Session(engine) as session:
        # Récupérer les classes du professeur
        professeur = get_user_by_cookie(session, session_cookie)
        if not professeur:
            return redirect(url_for('login_get'))
        
        if professeur.professeur != True:
            return redirect(url_for('dashboard'))
        # Convertir la liste des classes en Python
        niveau_classe = json.loads(professeur.niveau_classe)
        # Filtrer les demandes et les voeux par classe
        demandes = session.exec(select(DemandeAide).where(DemandeAide.classe.in_(niveau_classe))).all()
        voeux = session.exec(select(NotificationsVoeux).where(NotificationsVoeux.classe.in_(niveau_classe))).all()

    return render_template('notifications/index.html', demandes=demandes, voeux=voeux)