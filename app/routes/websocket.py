
"""
websocket.py

Ce fichier gère les fonctionnalités liées aux connexions WebSocket pour l'application Flask. 
Il utilise Flask-SocketIO pour permettre une communication bidirectionnelle en temps réel entre 
le serveur et les clients. Les principales fonctionnalités incluent :

1. Gestion des connexions WebSocket :
    - Détection des nouvelles connexions.
    - Gestion des déconnexions automatiques.

2. Gestion des rooms :
    - Attribution des utilisateurs à des rooms spécifiques basées sur leurs cookies de session.
    - Envoi de messages ciblés aux utilisateurs dans une room.

3. Suivi des utilisateurs connectés :
    - Mise à jour de l'état en ligne des utilisateurs dans la base de données.
    - Gestion des utilisateurs connectés par classe et par rôle (élève ou professeur).

4. Notifications en temps réel :
    - Envoi de notifications aux professeurs lorsque des élèves se connectent ou se déconnectent.
    - Calcul dynamique du nombre total d'élèves en ligne par classe et par professeur.

Ce fichier est essentiel pour gérer les interactions en temps réel entre les utilisateurs 
et fournir des mises à jour instantanées sur l'état des connexions dans l'application.
"""

from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
from flask_socketio import SocketIO, emit, join_room, leave_room
import threading
import time
from ds import send_discord_message


connected_users = {}

@socketio.on('connect')
def handle_connect():
    """Détecte une nouvelle connexion WebSocket"""
    print(f"Nouvelle connexion WebSocket: {request.sid}")


@socketio.on('join')
def handle_join(data):
    """L'utilisateur rejoint une room basée sur son cookie"""
    session_cookie = data.get('session_cookie')

    if not session_cookie:
        print("Aucun cookie de session fourni")
        return

    # Supprimer les anciens SID associés au même session_cookie
    for sid, cookie in list(connected_users.items()):
        if cookie == session_cookie:
            del connected_users[sid]

    # Associer request.sid au session_cookie
    connected_users[request.sid] = session_cookie

    join_room(session_cookie)

    with Session(engine) as session:
        # Récupérer l'utilisateur
        user = get_user_by_cookie(session, session_cookie)
        if user:

            if not user.online:
                send_discord_message("login_success", user.identifiant_unique, "/websocket", "0.0.0.0")
            user.online = True
            session.add(user)
            session.commit()

            # Si l'utilisateur est un professeur, ne pas envoyer de message
            if user.professeur:
                print(f"Professeur connecté: {user.identifiant_unique}")
            else:
                # Récupérer les classes de l'utilisateur (élève)
                user_classes = [user.niveau_classe]

                # Mettre à jour le nombre d'élèves en ligne pour chaque classe
                for classe in user_classes:
                    statement = select(Classes).where(Classes.classe == classe)
                    class_record = session.exec(statement).first()
                    if class_record:
                        class_record.online_student = (class_record.online_student or 0) + 1
                        session.add(class_record)
                        session.commit()

                # Récupérer les professeurs concernés
                statement = select(Superieurs).where(Superieurs.online == True)
                professors = session.exec(statement).all()

                # Calculer la somme des élèves en ligne pour chaque professeur
                for professor in professors:
                    professor_classes = json.loads(professor.niveau_classe)
                    if any(classe in professor_classes for classe in user_classes):
                        total_online_students = 0
                        for classe in professor_classes:
                            statement = select(Users).where(Users.online == True, Users.niveau_classe == classe)
                            class_record = session.exec(statement).all()
                            if class_record:
                                total_online_students += len(class_record)

                        # Envoyer un message aux professeurs concernés
                        for sid, cookie in connected_users.items():
                            if cookie == professor.cookie:
                                emit('message', {'msg': f'L\'utilisateur {user.identifiant_unique} a rejoint', 'total_online_students': total_online_students}, room=sid)

    print(f"Utilisateur connecté : {connected_users} (SID: {request.sid})")
    if user:
        with Session(engine) as session:
            professeurs = session.exec(select(Superieurs).where(Superieurs.professeur == True)).all()
            for professeur in professeurs:
                try:
                    if professeur.online:  # Vérifier que le professeur a un cookie de connexion valide
                        classes_professeur = json.loads(professeur.niveau_classe)
                        if user.niveau_classe in classes_professeur:
                            socketio.emit('online_student', {
                                'eleve_id': user.identifiant_unique,
                                'status': 'EN LIGNE',
                            }, room=professeur.cookie, namespace='/')
                            app.logger.info(f"Notification statut en ligne envoyée au professeur {professeur.identifiant_unique} pour l'élève {user.identifiant_unique}")
                except json.JSONDecodeError:
                    logging.error(f"Erreur de parsing JSON pour le professeur {professeur.identifiant_unique}")

    # Envoyer une confirmation au client
    emit('message', {'msg': f'Connecté à la room {session_cookie}'}, room=session_cookie)


@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    session_cookie = connected_users.get(sid)

    def delayed_disconnect(original_sid, original_cookie):
        socketio.sleep(5)

        # Si ce SID a été remplacé entre temps, alors on ne fait rien
        current_cookie = connected_users.get(original_sid)
        if current_cookie != original_cookie:
            return

        # Retirer l'utilisateur du tracking
        connected_users.pop(original_sid, None)

        with Session(engine) as session:
            user = get_user_by_cookie(session, original_cookie)
            if user:

                user.online = False
                session.add(user)
                session.commit()
            
                send_discord_message("utilisateur_deconnecte", user.identifiant_unique, "/websocket", "0.0.0.0")

                if not user.professeur:
                    user_classes = [user.niveau_classe]

                    for classe in user_classes:
                        statement = select(Classes).where(Classes.classe == classe)
                        class_record = session.exec(statement).first()
                        if class_record:
                            class_record.online_student = max((class_record.online_student or 0) - 1, 0)
                            session.add(class_record)
                            session.commit()

                    statement = select(Superieurs).where(Superieurs.online == True)
                    professors = session.exec(statement).all()

                    for professor in professors:
                        professor_classes = json.loads(professor.niveau_classe)
                        if any(classe in professor_classes for classe in user_classes):
                            total_online_students = 0
                            for classe in professor_classes:
                                statement = select(Users).where(Users.online == True, Users.niveau_classe == classe)
                                class_users = session.exec(statement).all()
                                total_online_students += len(class_users)

                            for other_sid, cookie in connected_users.items():
                                if cookie == professor.cookie:
                                    socketio.emit('message', {
                                        'msg': f"L'utilisateur {user.identifiant_unique} s'est déconnecté",
                                        'total_online_students': total_online_students
                                    }, room=other_sid)
        print(f"Utilisateur déconnecté (final) avec session_cookie: {original_cookie} (SID: {original_sid})")
        with Session(engine) as session:
            professeurs = session.exec(select(Superieurs).where(Superieurs.professeur == True)).all()
            for professeur in professeurs:
                try:
                    if professeur.online:  # Vérifier que le professeur a un cookie de connexion valide
                        classes_professeur = json.loads(professeur.niveau_classe)
                        if user.niveau_classe in classes_professeur:
                            socketio.emit('online_student', {
                                'eleve_id': user.identifiant_unique,
                                'status': 'HORS LIGNE',
                            }, room=professeur.cookie, namespace='/')
                            app.logger.info(f"Notification statut hors ligne envoyée au professeur {professeur.identifiant_unique} pour l'élève {user.identifiant_unique}")
                except json.JSONDecodeError:
                    logging.error(f"Erreur de parsing JSON pour le professeur {professeur.identifiant_unique}")

    # Appel avec les valeurs du moment
    socketio.start_background_task(delayed_disconnect, sid, session_cookie)
