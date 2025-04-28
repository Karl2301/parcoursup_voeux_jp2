"""
Ce fichier contient les fonctionnalités nécessaires pour gérer la suppression d'un professeur
dans l'application Flask. Il expose une route qui permet de supprimer un professeur de la base
de données en fonction de son identifiant unique.
Fonctionnalités principales :
- Vérification de l'authentification de l'utilisateur via un cookie de session.
- Validation des droits d'accès de l'utilisateur (seuls les administrateurs ou professeurs autorisés
    peuvent effectuer cette action).
- Recherche du professeur dans la base de données à l'aide de son identifiant unique.
- Suppression du professeur si celui-ci existe.
- Gestion des erreurs, telles que l'absence d'authentification, l'accès non autorisé ou un professeur
    introuvable.
Ce fichier est une partie essentielle du module de gestion des professeurs dans l'application.
"""

from flask import Flask, request, redirect, url_for, jsonify
from sqlmodel import Session, select, delete
from ext_config import *
import json
import logging
from ds import send_discord_message

def delete_prof():
    session_cookie = request.cookies.get('session_cookie')
    app.logger.info("Client IP: %s", get_client_ip())
    app.logger.info("Session cookie: %s", session_cookie)
    if not session_cookie:
        return redirect(url_for('login_get'))

    data = request.get_json()
    prof_id = data.get('identifiant_unique')

    with Session(engine) as session:
        user = get_user_by_cookie(session, session_cookie)
        if not user or not user.professeur or not user.admin:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        prof = session.exec(select(Superieurs).where(Superieurs.identifiant_unique == prof_id)).first()
        if not prof:
            return jsonify({'error': 'Professor not found'}), 404

        session.delete(prof)
        session.commit()
        send_discord_message("compte_prof_supprime", prof_id, get_url_from_request(request), get_client_ip())
        app.logger.info("Professor deleted successfully: %s", prof_id)
        return jsonify({'success': 'Professor deleted successfully'})