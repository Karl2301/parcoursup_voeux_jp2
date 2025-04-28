"""
Ce fichier contient la route pour la gestion de la connexion des utilisateurs dans l'application Flask.
Fonctionnalité principale:
- `login_post`: Cette fonction est appelée lorsqu'un utilisateur soumet le formulaire de connexion. Elle vérifie l'identifiant de l'utilisateur dans la base de données, génère un cookie de session unique, met à jour la base de données avec ce cookie, et le définit dans le navigateur de l'utilisateur.
Utilisation:
- Ce fichier est utilisé lorsque l'utilisateur tente de se connecter à l'application via le formulaire de connexion. Si l'identifiant est trouvé dans la base de données, l'utilisateur est redirigé vers la page d'accueil avec un cookie de session. Sinon, rien ne se passe.
"""

from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
import uuid
from flask_socketio import SocketIO, emit, join_room, leave_room
from ds import send_discord_message
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

def login_post():
    """
    data = request.get_json()  # Récupérer le contenu du POST en JSON
    identifiant = data.get('identifiant')
    """

    identifiant = request.form['identifiant']
    password = request.form['password']
    ip_address = get_client_ip()

    if not turnstile.verify():
        # Si le captcha échoue, renvoyer une erreur
        app.logger.warning("Captcha validation failed.")
        # return render_template("login/index.html", error="Captcha invalide.")
    
    app.logger.info("Client IP: %s", get_client_ip())
    app.logger.info("Login attempt for user: %s", identifiant)

    with Session(engine) as sessionuser:
        user = get_user_by_identifiant(sessionuser, identifiant)
        
        if not user:
            return render_template("login/index.html", error="Nom d'utilisateur ou mot de passe incorrect.")
        
        config = get_specific_config("disable_student_access")
        if config and user.professeur == False and user.admin == False: # Si l'accès élève est désactivé
            return render_template("login/index.html", error="Espace bloqué pour les élèves.")
        
        config = get_specific_config("disable_prof_access")
        if config and user.professeur == True and user.admin == False: # Si l'accès professeur est désactivé
            return render_template("login/index.html", error="Espace bloqué pour les professeurs.")
            
        if check_password_hash(user.password, password):
            # Générer un nouveau cookie de session
            new_session_cookie = str(uuid.uuid4())

            user.cookie = new_session_cookie
            user.online = True  # Mettre l'utilisateur en ligne
            
            sessionuser.add(user)
            sessionuser.commit()

            with Session(engine) as session:

                ip_record = session.exec(select(AdresseIP).where(AdresseIP.ip == ip_address)).first()
                ip_record_name = session.exec(select(AdresseIP).where(AdresseIP.username == identifiant)).first()
                if ip_record and ip_record_name:
                    app.logger.warning("IP address %s is listed.", ip_address)
                else: 
                    api_url = f"https://api.ipregistry.co/{ip_address}?key=ira_BIvtarKLy6yDc3Tw26YJ1QZR4SXfT14MSDgV"
                    response = requests.get(api_url)
                    if response.status_code == 200:
                        ip_data = response.json()
                        security_flags = [
                            "is_abuser",
                            "is_attacker",
                            "is_bogon",
                            "is_threat",
                            "is_tor_exit"
                        ]

                        # Vérifier si l'adresse IP est dans la liste noire
                        
                        for flag in security_flags:
                            if ip_data.get("security", {}).get(flag, False):
                                app.logger.warning("Security flag triggered: %s", flag)
                                return render_template("login/index.html", error="Connexion refusée pour des raisons de sécurité.")
                        # Enregistrer les données IP dans la base de données
                        ip_record = AdresseIP(
                            ip=ip_address,
                            username=user.identifiant_unique,
                            classe=user.niveau_classe,
                            country=ip_data.get("location", {}).get("country", "").get("name", ""),
                            region=ip_data.get("location", {}).get("region", "").get("name", ""),
                            city=ip_data.get("location", {}).get("city", ""),
                            latitude=ip_data.get("location", {}).get("latitude", 0),
                            longitude=ip_data.get("location", {}).get("longitude", 0),
                            data=json.dumps(ip_data, ensure_ascii=False),  # Serialize ip_data to JSON string
                            created_at=datetime.now(ZoneInfo("Europe/Paris")).strftime("%Y-%m-%d %H:%M:%S")  # Ajouter la date de création en UTC
                        )
                        session.add(ip_record)
                        session.commit()

                    else:
                        app.logger.warning("Failed to retrieve IP data. Status code: %s", response.status_code) 

            
            
            
            if user.professeur == True and user.deja_connecte == False: # Si l'utilisateur est un professeur et n'a pas encore configuré son mot de passe
                response = make_response(redirect(url_for('configure_prof_get')))
                response.set_cookie('session_cookie', new_session_cookie, samesite='Lax', secure=True)
            elif user.professeur == False and user.deja_connecte == False: # Si l'utilisateur est un élève et n'a pas encore configuré son mot de passe
                response = make_response(redirect(url_for('configure_password_get')))
                response.set_cookie('session_cookie', new_session_cookie, samesite='Lax', secure=True)
            #elif user.admin == True: # Si l'utilisateur est un administrateur
                #response = make_response(redirect(url_for('dashboard_admin')))
            else:
                app.logger.info("User logged in successfully: %s", user.identifiant_unique)
                send_discord_message("login_success", user.identifiant_unique, get_url_from_request(request))
                response = make_response(redirect(url_for('dashboard')))
                response.set_cookie('session_cookie', new_session_cookie, samesite='Lax', secure=True)
            return response
        else:
            error_message = "Nom d'utilisateur ou mot de passe incorrect."
            return render_template('login/index.html', error=error_message)
