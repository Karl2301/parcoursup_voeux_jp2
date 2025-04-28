"""
Ce fichier définit les routes pour la configuration du mot de passe dans l'application Flask.
Fonctionnalités principales :
- Affichage de la page permettant à l'utilisateur de configurer son mot de passe.
- Gestion de la logique pour vérifier si un utilisateur est connecté et autorisé à configurer son mot de passe.
- Validation des mots de passe saisis par l'utilisateur (confirmation et correspondance).
- Mise à jour sécurisée du mot de passe de l'utilisateur dans la base de données.
- Gestion des redirections en fonction de l'état de l'utilisateur (connecté, déjà configuré, ou non trouvé).
Ce fichier utilise les bibliothèques Flask, SQLModel, et Werkzeug pour gérer les sessions, 
les requêtes HTTP, et le hachage des mots de passe. Il s'appuie également sur des fonctions 
externes pour récupérer les informations utilisateur à partir des cookies de session.
"""

from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
from flask_socketio import SocketIO, emit, join_room, leave_room
import logging

# Route pour afficher la page de configuration du mot de passe



def configure_password_get():
    session_cookie = request.cookies.get('session_cookie')
    app.logger.info("Client IP: %s", get_client_ip())
    app.logger.info("Session cookie: %s", session_cookie)
    if session_cookie is None:
        flash("Vous devez être connecté pour configurer votre mot de passe.")
        return redirect(url_for('login_get'))
    
    with Session(engine) as session:
        user = get_user_by_cookie(session, session_cookie)

        if user:
            if user.deja_connecte == True:
                flash("Vous avez déjà configuré votre mot de passe.", "info")
                return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login_get'))

    return render_template('configure_password/index.html') 



def configure_password_post():
    session_cookie = request.cookies.get('session_cookie')
    app.logger.info("Client IP: %s", get_client_ip())
    app.logger.info("Session cookie: %s", session_cookie)

    if session_cookie is None:
        return jsonify({"error": "Session invalide. Veuillez vous reconnecter."}), 401

    password = request.form.get('password')
    password_confirm = request.form.get('confirm_password')

    # Validation des champs

    if password != password_confirm:
        return jsonify({"error": "Les mots de passe ne correspondent pas."}), 400
        
    if not password or not password_confirm:
        return jsonify({"error": "Tous les champs sont obligatoires."}), 400

    if len(password) < 8:
        return jsonify({"error": "Le mot de passe doit contenir au moins 8 caractères."}), 400
    
    if not any(char.isdigit() for char in password) or not any(char.isupper() for char in password):
        return jsonify({"error": "Le mot de passe doit contenir au moins 1 chiffre et 1 lettre majuscule."}), 400


    with Session(engine) as session:
        user = get_user_by_cookie(session, session_cookie)

        if user and user.deja_connecte == False:
            user.password = generate_password_hash(password)
            user.deja_connecte = True
            session.add(user)
            session.commit()
            app.logger.info("Password configured successfully for user: %s", user.identifiant_unique)
            return jsonify({"success": "Mot de passe configuré avec succès.", "redirect_url": url_for('dashboard')}), 200
        else:
            return jsonify({"error": "Utilisateur non trouvé ou déjà configuré."}), 404