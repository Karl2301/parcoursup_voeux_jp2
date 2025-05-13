"""
Ce fichier, `classes_prof.py`, gère les fonctionnalités liées à la gestion des classes 
par les professeurs dans l'application Flask. Il permet de :

1. Vérifier l'authentification et les permissions des utilisateurs via un cookie de session.
2. Restreindre l'accès aux fonctionnalités en fonction du rôle de l'utilisateur 
    (professeur ou élève).
3. Charger et afficher les informations des classes associées à un professeur spécifique.
4. Calculer et afficher des statistiques sur les élèves d'une classe, telles que :
    - Le nombre d'élèves connectés en ligne.
    - Le nombre d'élèves ayant validé leurs choix.
    - Le nombre d'élèves n'ayant pas encore validé leurs choix.
5. Fournir une interface utilisateur via un template HTML pour visualiser les informations 
    des classes et des élèves.

Ce fichier est essentiel pour la gestion des classes et des élèves dans le cadre de 
l'application, en assurant une séparation claire des responsabilités et des permissions 
entre les différents types d'utilisateurs.
"""

from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime

def classes_prof_get(class_name):
    session_cookie = request.cookies.get('session_cookie')
    if not session_cookie:
        return redirect(url_for('login_get'))

    with Session(engine) as session:
        # Récupérer l'utilisateur en fonction du cookie de session
        statement = select(Superieurs).where(Superieurs.cookie == session_cookie)
        user = session.exec(statement).one_or_none()
        if user and user.professeur != True :
                return redirect(url_for('dashboard'))
        statement_online_students = session.exec(
            select(Users).where(
                (Users.niveau_classe == class_name) &
                (Users.professeur == 0) &
                (Users.online == True)
            )
        )
        student_connected_for_class = len(statement_online_students.all())

        statement_validate_students = session.exec(
            select(Users).where(
                (Users.niveau_classe == class_name) &
                (Users.professeur == 0) &
                (Users.choix_validees == True)
            )
        )
        student_validate_for_class = len(statement_validate_students.all())

        if not user:
            return redirect(url_for('login_get'))

        # Vérifier si c'est un élève (accès interdit)
        if user.professeur == 0:
            flash("Accès interdit pour les élèves", "error")
            return redirect(url_for('dashboard'))

        # Charger la liste des classes du professeur
        prof_classe = json.loads(user.niveau_classe)
        if class_name not in prof_classe:
            flash("Vous n'avez pas accès à cette classe", "error")
            return redirect(url_for('dashboard'))

        # Récupérer les élèves appartenant à cette classe
        statement_eleves = select(Users).where(
            (Users.niveau_classe == class_name) & (Users.professeur == 0)
        )
        eleves = session.exec(statement_eleves).all()

        # Calculer le nombre d'élèves non validés
        nb_non_valide = len([eleve for eleve in eleves if not eleve.choix_validees])
        is_all_validate = nb_non_valide == 0

        return render_template('classes/index.html',
                               eleves=eleves,
                               class_name=class_name,
                               eleve_online_count=student_connected_for_class,
                               eleve_choix_validees_count=student_validate_for_class,
                               nb_non_valide=nb_non_valide,
                               is_all_validate=is_all_validate)
