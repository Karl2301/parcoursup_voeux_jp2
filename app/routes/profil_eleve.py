"""
Fichier: profil_eleve.py
Ce fichier gère les fonctionnalités liées à l'affichage du profil d'un élève 
dans le cadre de l'application Parcoursup Voeux. Il contient les routes et 
logiques nécessaires pour permettre aux professeurs de consulter les informations 
des élèves auxquels ils ont accès.
Fonctionnalités principales :
- Vérification de la session utilisateur via un cookie pour garantir la sécurité.
- Validation des permissions d'accès : seuls les professeurs peuvent accéder à 
    cette page, et uniquement pour les élèves des classes qui leur sont attribuées.
- Récupération des informations détaillées d'un élève spécifique, tout en excluant 
    les données sensibles comme le mot de passe.
- Affichage des informations de l'élève et de ses choix d'établissements via un 
    template HTML dédié.
Ce fichier assure également une gestion des erreurs et des redirections appropriées 
en cas de problème, comme un accès non autorisé ou un élève introuvable.
"""

from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
from flask_socketio import SocketIO, emit, join_room, leave_room




def profil_eleve_get(eleve_id):
    # Vérifier la présence du cookie de session
    session_cookie = request.cookies.get('session_cookie')
    app.logger.info("Client IP: %s", get_client_ip())
    app.logger.info("Session cookie: %s", session_cookie)
    if not session_cookie:
        return redirect(url_for('login_get'))

    with Session(engine) as session:
        
        user = get_user_by_cookie(session, session_cookie)

        if not user:
            return redirect(url_for('login_get'))

        # Seuls les professeurs ont accès à cette page
        if user.professeur == False:
            flash("Accès interdit pour les élèves", "error")
            return redirect(url_for('dashboard'))

        # Recup la liste des classes auxquelles le professeur a accès
        user_classes = json.loads(user.niveau_classe)

        # Récupérer l'élève dont l'identifiant est fourni et vérifier qu'il s'agit bien d'un élève
        eleve_statement = select(Users).where(Users.identifiant_unique == eleve_id, Users.professeur == 0)
        eleve = session.exec(eleve_statement).one_or_none()

        if not eleve:
            flash("Élève non trouvé", "error")
            return redirect(url_for('dashboard'))

        # Vérifier que l'élève appartient bien à une classe accessible par le professeur
        if eleve.niveau_classe not in user_classes:
            flash("Vous n'avez pas accès à cette classe", "error")
            return redirect(url_for('dashboard'))

        # Exclure le mot de passe de la réponse
        eleve_data = eleve.model_dump()
        eleve_data.pop('password', None)

        # Afficher le profil de l'élève via le template dédié
        app.logger.info("Profil de l'élève affiché: %s", eleve_id)
        return render_template('eleve/index.html', eleve=eleve_data, voeux=json.loads(eleve.voeux_etablissements))