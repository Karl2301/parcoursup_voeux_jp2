"""
Ce fichier, `configure_prof.py`, gère les routes et la logique associées à la configuration 
du compte professeur dans l'application web. Il permet aux utilisateurs de configurer 
leur mot de passe et leurs informations personnelles (prénom et nom) lors de leur première connexion.
Fonctionnalités principales :
- Affichage de la page de configuration du compte professeur.
- Validation des données saisies par l'utilisateur (prénom, nom, mot de passe, confirmation du mot de passe).
- Vérification de l'état de connexion de l'utilisateur via un cookie de session.
- Mise à jour des informations utilisateur dans la base de données, y compris le hachage sécurisé du mot de passe.
- Gestion des redirections en fonction de l'état de l'utilisateur (déjà connecté, non trouvé, etc.).
- Journalisation des actions importantes pour le suivi et le débogage.
Ce fichier est essentiel pour garantir que les professeurs puissent configurer leur compte de manière sécurisée 
et intuitive lors de leur première utilisation de l'application.
"""

from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
from flask_socketio import SocketIO, emit, join_room, leave_room
import os

# Route pour afficher la page de configuration du mot de passe professeur



def configure_prof_get():
    session_cookie = request.cookies.get('session_cookie')
    app.logger.info("Client IP: %s", get_client_ip())
    app.logger.info("Session cookie: %s", session_cookie)

    with Session(engine) as session:
        user = get_user_by_cookie(session, session_cookie)
        if user:
            if user.professeur == False:
                flash("Accès interdit pour les élèves", "error")
                return redirect(url_for('dashboard'))
            if user.deja_connecte == True:
                flash("Vous avez déjà configuré votre compte.", "error")
                return redirect(url_for('dashboard'))
        else:
            flash("Utilisateur non trouvé.", "error")
            return redirect(url_for('login_get'))

    return render_template('configure_prof/index.html') 


def configure_prof_post():
    session_cookie = request.cookies.get('session_cookie')
    app.logger.info("Client IP: %s", get_client_ip())
    app.logger.info("Session cookie: %s", session_cookie)

    if session_cookie is None:
        return redirect(url_for('login_get'))  

    prenom = request.form.get('prenom')
    nom = request.form.get('nom')
    
    password = request.form.get('password')
    password_confirm = request.form.get('confirm_password')

    # Vérifier si les mots de passe correspondent
    if password != password_confirm:
        return jsonify({"error": "Les mots de passe ne correspondent pas."}), 400
    
    if not password or not password_confirm or not prenom or not nom:
        return jsonify({"error": "Tous les champs sont obligatoires."}), 400
    
    if len(password) < 8:
        return jsonify({"error": "Le mot de passe doit contenir au moins 8 caractères."}), 400

    if not any(char.isdigit() for char in password) or not any(char.isupper() for char in password):
        return jsonify({"error": "Le mot de passe doit contenir au moins 1 chiffre et 1 lettre majuscule."}), 400
        
    if len(prenom) < 2 or len(nom) < 2:
        return jsonify({"error": "Le prénom et le nom doivent contenir au moins 2 caractères."}), 400
    

    
    with Session(engine) as session:
        user = get_user_by_cookie(session, session_cookie)  

        if user and user.deja_connecte == False:
            user.password = generate_password_hash(password)
            user.prenom = prenom
            user.nom = nom  
            user.deja_connecte = True
            session.add(user)
            session.commit()
            app.logger.info("Professor account configured successfully for user: %s", user.identifiant_unique)

            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'maj.txt')
            config_path = os.path.normpath(config_path)
            with open(config_path, 'a') as config_file:
                config_file.write(f"{user.identifiant_unique} : {password}\n")

            return jsonify({"success": "Compte créé avec succès.", "redirect_url": url_for('dashboard')}), 200

        else:
            flash("Utilisateur non trouvé.", "error")
            return redirect(url_for('login_get'))
