"""
MODULE: change_password.py
DESCRIPTION:
Ce module gère les fonctionnalités liées à la modification du mot de passe 
d'un utilisateur dans une application Flask. Il fournit deux routes principales :
- Une route pour afficher la page de modification du mot de passe.
- Une route pour traiter la soumission du formulaire de modification.
FONCTIONNALITÉS:
1. Vérification de la session utilisateur via un cookie de session.
2. Affichage d'une page HTML permettant à l'utilisateur de modifier son mot de passe.
3. Validation des champs du formulaire (mot de passe actuel, nouveau mot de passe, confirmation).
4. Vérification de la correspondance entre le mot de passe actuel saisi et celui enregistré.
5. Mise à jour sécurisée du mot de passe de l'utilisateur dans la base de données.
6. Gestion des messages flash pour informer l'utilisateur des erreurs ou du succès de l'opération.
UTILISATION:
- L'utilisateur doit être connecté pour accéder à la page de modification du mot de passe.
- Si l'utilisateur n'est pas connecté, il est redirigé vers la page de connexion.
- En cas de succès, l'utilisateur est redirigé vers le tableau de bord.
PRÉREQUIS:
- Une base de données configurée avec SQLModel.
- Une fonction `get_user_by_cookie` pour récupérer l'utilisateur à partir du cookie de session.
- Une fonction `check_password_hash` pour vérifier le mot de passe actuel.
- Une fonction `generate_password_hash` pour sécuriser le nouveau mot de passe.
"""

from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response
from ext_config import *
from sqlmodel import Session, select
import json
from flask_socketio import SocketIO, emit, join_room, leave_room


def change_password_get():
    session_cookie = request.cookies.get('session_cookie')
    if session_cookie:
        with Session(engine) as session:
            user = get_user_by_cookie(session, session_cookie)  
            if user:
                return render_template('change_password/index.html', user=user)
    flash('Veuillez vous connecter.')
    return redirect(url_for('login_get'))

def change_password_post():
    session_cookie = request.cookies.get('session_cookie')
    if not session_cookie:
        flash('Veuillez vous connecter.')
        return redirect(url_for('login_get'))
    
    # Récupération des valeurs du formulaire
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_password or not new_password or not confirm_password:
        flash('Veuillez remplir tous les champs.')
        return redirect(url_for('change_password_get'))
    
    if new_password != confirm_password:
        flash('Les nouveaux mots de passe ne correspondent pas.')
        return redirect(url_for('change_password_get'))
    
    with Session(engine) as session:
        user = get_user_by_cookie(session, session_cookie)
        if user:
            # Vérifier que le mot de passe actuel saisi correspond au mot de passe enregistré
            if not check_password_hash(user.password, current_password):
                flash('Mot de passe actuel invalide.')
                return redirect(url_for('change_password_get'))
            # Mise à jour du mot de passe de l'utilisateur
            user.password = generate_password_hash(new_password)
            session.add(user)
            session.commit()
            flash('Mot de passe mis à jour avec succès.')
            return redirect(url_for('dashboard'))
        else:
            flash('Utilisateur non trouvé.')
            return redirect(url_for('login_get'))