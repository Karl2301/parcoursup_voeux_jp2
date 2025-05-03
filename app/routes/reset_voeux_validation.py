"""
reset_voeux_validation.py
Ce fichier gère la réinitialisation des choix validés (voeux) pour un utilisateur spécifique
dans le cadre de l'application Parcoursup. Il fournit une route permettant aux utilisateurs
ayant des privilèges (professeurs ou administrateurs) de réinitialiser les voeux d'un autre
utilisateur.
Fonctionnalités :
- Vérification de l'authentification de l'utilisateur via un cookie de session.
- Validation des privilèges de l'utilisateur (professeur ou administrateur).
- Réinitialisation des choix validés pour un utilisateur donné.
- Gestion des erreurs et retour d'une réponse JSON appropriée.
Ce fichier est une partie essentielle de la gestion des voeux dans l'application, permettant
de corriger ou de réinitialiser les choix validés en cas de besoin.
"""

from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
import uuid
from flask_socketio import SocketIO, emit, join_room, leave_room

def reset_voeux_validation_post():
    session_cookie = request.cookies.get('session_cookie')
    
    with Session(engine) as sessionuser:
        user = get_user_by_cookie(sessionuser, session_cookie)
        
        if not user:
            return redirect(url_for('login_get'))
        
        config = get_specific_config("disable_prof_reset_voeux")
        if config and user.professeur == True and user.admin == False: # Si l'accès professeur est désactivé
            return jsonify({"error": "Reset des veoux bloqué pour les professeurs."}), 403

        if user.professeur == True or user.admin == True:

            
            data = request.get_json()
            user_to_reset = data.get('user_to_reset')
            
            if not user_to_reset:
                return jsonify({"error": "user_to_reset is required"}), 400
            
            user_to_reset = get_user_by_identifiant(sessionuser, user_to_reset)
            user_to_reset.choix_validees = False
            user_to_reset.voeux_validation = None
            sessionuser.add(user_to_reset)
            sessionuser.commit()

            return jsonify({"success": "Voeux de l'utilisateur réinitialisés avec succès."}), 200
        else:
            return jsonify({"error": "Vous n'êtes pas autorisé à effectuer cette action."}), 403
    return jsonify({"error": "Une erreur s'est produite lors de la réinitialisation des voeux de l'utilisateur."}), 500
            