"""
Ce fichier gère les fonctionnalités liées au changement de nom d'utilisateur 
dans l'application Flask. Il contient deux fonctions principales :
1. `change_username_get` : 
    - Permet d'afficher la page de changement de nom d'utilisateur.
    - Vérifie si l'utilisateur est connecté via un cookie de session.
    - Vérifie si l'utilisateur est un professeur avant de lui permettre d'accéder à la page.
    - Redirige vers la page de connexion ou le tableau de bord en cas d'erreur.
2. `change_username_post` : 
    - Permet de traiter la soumission du formulaire de changement de nom d'utilisateur.
    - Vérifie les champs du formulaire, la correspondance des noms d'utilisateur, 
      et la validité du mot de passe actuel.
    - Met à jour le nom d'utilisateur dans la base de données si toutes les vérifications sont réussies.
    - Retourne une réponse JSON indiquant le succès ou l'échec de l'opération.
Ce fichier utilise Flask pour la gestion des requêtes HTTP, SQLModel pour les interactions 
avec la base de données, et des fonctions utilitaires pour la gestion des utilisateurs 
et des mots de passe.
"""

from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response
from ext_config import *
from sqlmodel import Session, select
import json
from flask_socketio import SocketIO, emit, join_room, leave_room


def change_username_get():
    session_cookie = request.cookies.get('session_cookie')
    if session_cookie:
        with Session(engine) as session:
            user = get_user_by_cookie(session, session_cookie)  
            if user:
                if not user.professeur:
                    flash('Vous n\'êtes pas professeur.')
                    return redirect(url_for('dashboard'))
                
                return render_template('change_username/index.html', user=user, user_username=user.identifiant_unique)
            
    flash('Veuillez vous connecter.')
    return redirect(url_for('login_get'))

def change_username_post():
    session_cookie = request.cookies.get('session_cookie')
    if not session_cookie:
        flash('Veuillez vous connecter.')
        return redirect(url_for('login_get'))
    
    # Récupération des valeurs du formulaire
    current_password = request.form.get('current_password')
    new_username = request.form.get('new_username')
    confirm_username = request.form.get('confirm_username')
    
    if not current_password or not new_username or not confirm_username:
        flash('Veuillez remplir tous les champs.')
        return jsonify({'success': False , 'message': 'Veuillez remplir tous les champs.'})
    
    if new_username != confirm_username:
        flash('Les nouveaux username ne correspondent pas.')
        return jsonify({'success': False, 'message': 'Les nouveaux noms d\'utilisateurs ne correspondent pas.'})
    
    with Session(engine) as session:
        user = get_user_by_cookie(session, session_cookie)
        if user:
            if not user.professeur:
                    flash('Vous n\'êtes pas professeur.')
                    return redirect(url_for('dashboard'))
            # Vérifier que le mot de passe actuel saisi correspond au mot de passe enregistré
            if not check_password_hash(user.password, current_password):
                flash('Mot de passe actuel invalide.')
                return jsonify({'success': False, 'message': 'Mot de passe actuel invalide.'})
            # Mise à jour du mot de passe de l'utilisateur
            user.identifiant_unique = new_username
            session.add(user)
            session.commit()
            return jsonify({'success': True})
        else:
            return redirect(url_for('login_get'))