"""
Fichier: delete_notifs.py

Ce fichier contient les routes et les fonctions nécessaires pour gérer la suppression
des demandes d'aide dans l'application Flask. Il est principalement utilisé pour 
permettre aux utilisateurs ayant les droits appropriés (comme les professeurs) 
de supprimer des demandes spécifiques.

Fonctionnalités :
- Vérification de la session utilisateur via un cookie pour s'assurer que l'utilisateur est connecté.
- Validation des droits de l'utilisateur pour effectuer des actions de suppression.
- Suppression d'une demande d'aide spécifique de la base de données si les conditions sont remplies.
- Gestion des redirections et des messages flash en cas d'erreurs ou de permissions insuffisantes.

Ce fichier est une partie essentielle de la gestion des notifications et des demandes d'aide
dans l'application.
"""

from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
import uuid
from flask_socketio import SocketIO, emit, join_room, leave_room

def delete_demande(id):
    session_cookie = request.cookies.get('session_cookie')
    if session_cookie is None:
        flash("Vous devez être connecté pour supprimer une demande.")
        return redirect(url_for('login_get'))

    with Session(engine) as session:
        user = get_user_by_cookie(session, session_cookie)
        if user:
            if user.professeur == True:
                demande = session.get(DemandeAide, id)  # Récupérer l'instance de la demande
                if demande:
                    session.delete(demande)
                    session.commit()
            else:
                flash("Vous n'avez pas les droits pour supprimer cette demande.")
                return redirect(url_for('home'))
        else:
            return redirect(url_for('login_get'))

    return {'success': True}