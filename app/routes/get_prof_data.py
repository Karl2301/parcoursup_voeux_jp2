"""
Ce fichier définit une route Flask pour récupérer les données d'un professeur
dans le cadre de l'application Parcoursup Voeux JP2. 
Fonctionnalités :
- Vérifie la présence d'un cookie de session pour authentifier l'utilisateur.
- Redirige l'utilisateur vers la page de connexion si le cookie de session est absent ou invalide.
- Vérifie si l'utilisateur connecté dispose des droits administratifs.
- Permet de récupérer les informations détaillées d'un professeur à partir de son identifiant unique.
- Retourne les données du professeur sous forme de réponse JSON, incluant des informations telles que 
    le niveau de classe, le statut en ligne, le thème du tableau de bord, et les informations personnelles.
Gestion :
- Gère les erreurs liées à l'absence d'identifiant de professeur ou à un professeur introuvable.
- Assure que seules les données accessibles par un administrateur sont retournées.
"""

from flask import Flask, request, redirect, url_for, jsonify
from sqlmodel import Session, select
from ext_config import *
import json
import logging

def get_prof_data():
    session_cookie = request.cookies.get('session_cookie')
    if not session_cookie:
        return redirect(url_for('login_get'))
    
    with Session(engine) as session:
        user = get_user_by_cookie(session, session_cookie)

        if not user:
            return redirect(url_for('login_get'))
        
        if not user.admin:
            return redirect(url_for('dashboard'))

        prof_id = request.args.get('id')
        if not prof_id:
            return jsonify({'error': 'No professor ID provided'}), 400

        with Session(engine) as session:
            prof = session.exec(select(Superieurs).where(Superieurs.identifiant_unique == prof_id)).first()
            if not prof:
                return jsonify({'error': 'Professor not found'}), 404

            admin = session.exec(select(Superieurs).where(Superieurs.admin == True)).first()
            classe_available = json.loads(admin.niveau_classe)
            classe_selected = json.loads(prof.niveau_classe)

            prof_data = {
                'identifiant_unique': prof.identifiant_unique,
                'niveau_classe': classe_selected,
                'classe_available': classe_available,
                'online': prof.online,
                'deja_connecte': prof.deja_connecte,
                'dashboard_theme': prof.dashboard_theme,
                'nom': prof.nom,
                'prenom': prof.prenom,
                'email': prof.email
            }

            return jsonify(prof_data)


