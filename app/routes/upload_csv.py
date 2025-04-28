"""
upload_csv.py
Ce fichier gère les fonctionnalités liées à l'importation de fichiers CSV dans l'application Flask.
Il permet aux administrateurs de téléverser un fichier CSV contenant des informations sur les utilisateurs
et leurs vœux d'établissement, de traiter ces données, et de les insérer ou mettre à jour dans la base de données.
Fonctionnalités principales :
- Vérification des droits d'accès de l'utilisateur (seuls les administrateurs peuvent accéder à ces fonctionnalités).
- Téléversement et validation des fichiers CSV.
- Décodage et traitement des données contenues dans le fichier CSV.
- Ajout ou mise à jour des utilisateurs et de leurs vœux dans la base de données.
Ce fichier inclut également des mécanismes de journalisation pour suivre les actions effectuées
et détecter les éventuelles erreurs lors du traitement des fichiers CSV.
"""

from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
import uuid
from flask_socketio import SocketIO, emit, join_room, leave_room
import csv
from io import StringIO
import logging

def upload_csv_get():
    session_cookie = request.cookies.get('session_cookie')
    app.logger.info("Client IP: %s", get_client_ip())
    app.logger.info("Session cookie: %s", session_cookie)

    with Session(engine) as session:
        user = get_user_by_cookie(session, session_cookie)
        if not user:
            return redirect(url_for('login_get'))

        if not user.admin:
            flash("Vous n'êtes pas autorisé à accéder à cette page.", "error")
            return redirect(url_for('dashboard'))
        
    return render_template('upload_csv/index.html')

def upload_csv():
    app.logger.info("Client IP: %s", get_client_ip())

    session_cookie = request.cookies.get('session_cookie')
    app.logger.info("Session cookie: %s", session_cookie)

    with Session(engine) as session:
        user = get_user_by_cookie(session, session_cookie)
        if not user:
            return redirect(url_for('login_get'))

        if not user.admin:
            flash("Vous n'êtes pas autorisé à accéder à cette page.", "error")
            return redirect(url_for('dashboard'))
        
    if "file" not in request.files:
        app.logger.error("Aucun fichier reçu")
        return jsonify({"error": "Aucun fichier reçu"}), 400

    file = request.files["file"]
    if file.filename == "":
        app.logger.error("Nom de fichier invalide")
        return jsonify({"error": "Nom de fichier invalide"}), 400

    content = file.read().decode("utf-8")
    app.logger.info("Fichier CSV reçu et décodé")
    
    with Session(engine) as session:
        result = process_csv(content, session)

    if result["status"] == "partial":
        return jsonify({
            "message": "Importation partielle terminée avec des erreurs.",
            "errors": result["errors"]
        }), 400

    app.logger.info("Utilisateurs créés/mis à jour avec succès")
    return jsonify({"message": "Utilisateurs créés/mis à jour avec succès"})


def process_csv(file_content, session):
    reader = csv.DictReader(StringIO(file_content))
    user_data = {}
    errors = []  # Liste pour stocker les erreurs
    app.logger.info("Processing CSV file...")

    for row_number, row in enumerate(reader, start=1):
        try:
            # Validation des champs obligatoires
            classe = row.get("Classe", "").strip()
            numero = row.get("Numéro", "").strip()
            etablissement = row.get("Etablissement", "").strip()
            ville = row.get("Ville", "").strip()
            type_formation = row.get("Type de formation", "").strip()
            formation = row.get("Libellé formation d'affectation", "").strip()

            if not numero:
                errors.append(f"Ligne {row_number}: Numéro manquant")
                continue  # Ignorer les lignes sans numéro valide

            app.logger.info(f"Processing row {row_number} for user: {numero}")

            voeux = {
                "row_number": len(user_data.get(numero, [])) + 1,
                "school": etablissement,
                "city": ville,
                "degree": type_formation,
                "specialization": formation,
                "enable": False
            }

            if numero in user_data:
                user_data[numero]["voeux"].append(voeux)
            else:
                user_data[numero] = {
                    "classe": classe,
                    "voeux": [voeux]
                }
        except Exception as e:
            error_message = f"Ligne {row_number}: Erreur lors du traitement ({str(e)})"
            app.logger.error(error_message)
            errors.append(error_message)

    # Ajout/Mise à jour en base de données
    for numero, data in user_data.items():
        try:
            app.logger.info(f"Processing user: {numero}")
            user = session.exec(select(Users).where(Users.identifiant_unique == numero)).one_or_none()
            if user:
                user.voeux_etablissements = json.dumps(data["voeux"])
            else:
                user = Users(
                    niveau_classe=data["classe"],
                    password=generate_password_hash("EleveMDP"),
                    online=False,
                    deja_connecte=False,
                    choix_validees=False,
                    admin=False,
                    professeur=False,
                    didacticiel=False,
                    identifiant_unique=numero,
                    voeux_etablissements=json.dumps(data["voeux"]),
                )
                session.add(user)
        except Exception as e:
            error_message = f"Utilisateur {numero}: Erreur lors de l'ajout/mise à jour ({str(e)})"
            app.logger.error(error_message)
            errors.append(error_message)

    session.commit()
    app.logger.info("Database commit successful")

    # Retourner les erreurs pour un rapport détaillé
    if errors:
        app.logger.warning("Des erreurs ont été détectées lors du traitement du fichier CSV")
        return {"status": "partial", "errors": errors}
    else:
        return {"status": "success", "errors": []}
    reader = csv.DictReader(StringIO(file_content))
    user_data = {}
    app.logger.info("Processing CSV file...")

    for row in reader:
        classe = row["Classe"]
        numero = row["Numéro"]
        etablissement = row["Etablissement"]
        ville = row["Ville"]
        type_formation = row["Type de formation"]
        formation = row["Libellé formation d'affectation"]

        if not numero:
            continue  # Ignorer les lignes sans numéro valide
        app.logger.info(f"Processing row for user: {numero}")
        voeux = {
            "row_number": len(user_data.get(numero, [])) + 1,
            "school": etablissement,
            "city": ville,
            "degree": type_formation,
            "specialization": formation,
            "enable": False
        }
        if numero in user_data:
            user_data[numero]["voeux"].append(voeux)
        else:
            user_data[numero] = {
                "classe": classe,  # Associer la classe à l'utilisateur
                "voeux": [voeux]
            }

    # Ajout/Mise à jour en base de données
    for numero, data in user_data.items():
        app.logger.info(f"Processing user: {numero}")
        user = session.exec(select(Users).where(Users.identifiant_unique == numero)).one_or_none()
        if user:
            user.voeux_etablissements = json.dumps(data["voeux"])
        else:
            user = Users(
                niveau_classe=data["classe"],  # Utiliser la classe correcte
                password=generate_password_hash("EleveMDP"),
                online=False,
                deja_connecte=False,
                choix_validees=False,
                admin=False,
                professeur=False,
                didacticiel=False,
                identifiant_unique=numero,
                voeux_etablissements=json.dumps(data["voeux"]),
            )
            session.add(user)

    session.commit()
    app.logger.info("Database commit successful")