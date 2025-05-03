"""
Ce fichier, `save_prof_data.py`, fait partie des routes de l'application Flask et gère la sauvegarde 
et la mise à jour des données des professeurs dans la base de données.

Fonctionnalités principales :
- Vérifie la présence d'un cookie de session pour authentifier l'utilisateur.
- Récupère les données JSON envoyées via une requête HTTP POST.
- Ajoute un nouveau professeur dans la base de données si celui-ci n'existe pas encore.
- Met à jour les informations d'un professeur existant si son identifiant unique est trouvé.
- Gère les champs tels que le prénom, le nom, l'email, le statut de connexion, le niveau de classe, 
    et le mot de passe par défaut.
- Utilise SQLModel pour interagir avec la base de données.

Ce fichier est essentiel pour la gestion des données des professeurs dans l'application, 
permettant de centraliser et de maintenir à jour les informations nécessaires.
"""

from flask import Flask, request, redirect, url_for, jsonify
from sqlmodel import Session, select
from ext_config import *
import json
import logging
from ds import send_discord_message
from create_classes import create_all_classes

def save_prof_data():
    session_cookie = request.cookies.get('session_cookie')
    if not session_cookie:
        return redirect(url_for('login_get'))

    data = request.get_json()
    prof_id = data.get('identifiant_unique')
    prenom = data.get('prenom')
    nom = data.get('nom')
    niveau_classe = json.dumps(data.get('niveau_classe'))
    admin = data.get('admin')



    with Session(engine) as session:
        prof = session.exec(select(Superieurs).where(Superieurs.identifiant_unique == prof_id)).first()
        if not prof:
            # Ajouter un nouveau professeur
            password = ""
            if not admin:
                password="ProfMDP"
            else:
                password="AdminMDP"

            new_prof = Superieurs(
                identifiant_unique=prof_id,
                password=generate_password_hash(password),
                prenom=prenom,
                nom=nom,
                niveau_classe=niveau_classe,
                deja_connecte=False,
                online=False,
                admin=admin,

            )

            send_discord_message("creation_compte_prof", prof_id, get_url_from_request(request), get_client_ip())
            session.add(new_prof)
        else:
            if prof.deja_connecte == False and (check_password_hash(prof.password, "ProfMDP") or check_password_hash(prof.password, "AdminMDP")):
                if not admin:
                    password="ProfMDP"
                else:
                    password="AdminMDP"
                prof.password = generate_password_hash(password)

            prof.prenom = prenom
            prof.nom = nom
            prof.online = False
            prof.niveau_classe = niveau_classe
            prof.admin = admin

            session.add(prof)

        session.commit()
        create_all_classes()
        return jsonify({'success': 'Professor data updated successfully'})