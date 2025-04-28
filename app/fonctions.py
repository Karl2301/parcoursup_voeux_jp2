from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from SQLClassSQL import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
from flask_socketio import SocketIO, emit, join_room, leave_room
import requests
import os
from datetime import datetime, timedelta
import subprocess

def get_user_by_cookie(db_session: Session, cookie_value: str):
    """
    Vérifie si un cookie est présent dans la table Users ou Professeurs.
    Retourne les données associées ou None si non trouvé.
    """

    if cookie_value == None:
        return None
    # Vérifier dans la table Users
    user = db_session.exec(select(Users).where(Users.cookie == cookie_value)).one_or_none()
    if user:
        return user
    
    # Vérifier dans la table Professeurs
    professor = db_session.exec(select(Superieurs).where(Superieurs.cookie == cookie_value)).one_or_none()
    if professor:
        return professor

    
    return None


def get_user_by_identifiant(db_session: Session, identifiant: str):
    """
    Vérifie si un cookie est présent dans la table Users ou Professeurs.
    Retourne les données associées ou None si non trouvé.
    """

    if identifiant == None:
        return None
    
    # Vérifier dans la table Users
    user = db_session.exec(select(Users).where(Users.identifiant_unique == identifiant)).one_or_none()
    if user:
        return user
    
    # Vérifier dans la table Professeurs
    professor = db_session.exec(select(Superieurs).where(Superieurs.identifiant_unique == identifiant)).one_or_none()
    if professor:
        return professor
    
    
    return None

def get_client_ip():
    try:
        if request.headers.get('X-Forwarded-For'):
            ip = request.headers.get('X-Forwarded-For').split(',')[0]
        else:
            ip = request.remote_addr
        return ip
    except Exception as e:
        print(f"An error occurred while retrieving the client IP: {e}")
        return None

def get_url_from_request(request_in):
    """
    Récupère l'URL d'origine (Origin) depuis les en-têtes de la requête.
    Si l'en-tête Origin n'est pas présent, retourne None.
    """
    try:
        origin = request_in.headers.get('Referer')  # Récupère l'en-tête Origin
        if origin:
            return origin
        else:
            # Si Origin n'est pas présent, retourne une valeur par défaut ou None
            return None
    except Exception as e:
        print(f"An error occurred while retrieving the URL from the request: {e}")
        return None
    

def get_app_config():
    """
    Récupère la configuration de l'application depuis le fichier config.json.
    Retourne un dictionnaire contenant la configuration.
    """
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    config_path = os.path.normpath(config_path)
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    return config


def send_email_when_users_confirmed(db_session: Session):

    # Récupérer tous les superieurs avec want_email à True
    superieurs_with_email = db_session.exec(select(Superieurs).where(Superieurs.want_email == True)).all()

    # Lister tous les emails de ces utilisateurs
    email_list = [superieur.email for superieur in superieurs_with_email]
    cc_emails = [{"email": email} for email in email_list]

    url = "https://api.brevo.com/v3/smtp/email"

    for email in cc_emails:
        print(email)
        payload = {
            "sender": {
                "name": "Voeux-JP2",
                "email": "no-reply@voeux-jp2.fr"
            },
            "subject": "Validations des voeux",
            "htmlContent": "<!DOCTYPE html><html>  <body style='font-family: Arial, sans-serif; line-height: 1.6;'>    <h2>Finalisation des vœux des élèves</h2>    <p>      Bonjour,    </p>    <p>      Nous vous informons que <strong>l'ensemble des élèves ont désormais finalisé et validé leurs vœux</strong>.      Les statistiques associées ainsi que les fichiers PDF générés sont à présent <strong>figés et ne pourront plus être modifiés</strong>.    </p>    <p>      Vous pouvez dès à présent consulter les données définitives via votre espace personnel sur la plateforme.    </p>  <p>https://www.voeux-jp2.fr  <p>      Bien cordialement,<br/>      Voeux-JP2    </p>  </body></html>",
            "type": "classic",
            "to": [
                { "email": email.get("email"), "name": "Admin" }
            ],
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": os.getenv("SMTP_API_KEY")
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while sending the email: {e}")

        print(response.text)


def send_email_to_prof_when_all_classe_validate(db_session: Session, classe: str):

    # Récupérer tous les superieurs avec want_email à True
    superieurs = db_session.exec(select(Superieurs).where(Superieurs.want_email == True, Superieurs.admin == False)).all()

    # Filtrer les résultats en fonction de niveau_classe
    superieurs_with_email = [s for s in superieurs if classe in s.niveau_classe]

    # Lister tous les emails des utilisateurs sélectionnés
    email_list = [superieur.email for superieur in superieurs_with_email]
    cc_emails = [{"email": email} for email in email_list]

    print(cc_emails)
    if not cc_emails:
        print("No CCi emails to send.")
        return
    
    for email in cc_emails:
        print(email)
        # Vérifier si la liste est vide                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
        url = "https://api.brevo.com/v3/smtp/email"

        payload = {
            "sender": {
                "name": "Voeux-JP2",
                "email": "no-reply@voeux-jp2.fr"
            },
            "subject": "Validations des voeux",
            "htmlContent":"<!DOCTYPE html><html>  <body style='font-family: Arial, sans-serif; line-height: 1.6;'>    <h2>Finalisation des vœux des élèves</h2>    <p>      Bonjour,    </p>    <p>      Nous vous informons que <strong>tous les élèves de la classe "+ classe +" ont désormais finalisé et validé leurs vœux</strong>.</p> <p>Les fichiers PDF et XLSX générés sont à présent <strong>figés et ne pourront plus être modifiés</strong>.    </p>    <p>      Vous pouvez dès à présent consulter les données définitives via votre espace personnel sur la plateforme.    </p>    <p>      https://www.voeux-jp2.fr    </p>    <p>      Bien cordialement,<br/>      Voeux-JP2    </p>  </body></html>",
            "type": "classic",
            "to": [
                { "email": email.get("email"), "name": "Prof" }
            ],
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": os.getenv("SMTP_API_KEY")
        }
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            print(response.text)
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while sending the email: {e}")





def get_specific_config(config_name: str):
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    config_path = os.path.normpath(config_path)
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
        config_value = config.get(config_name)
    return config_value



def get_cloudflare_stats():
    API_TOKEN = os.getenv("API_TOKEN")
    ZONE_ID = os.getenv("ZONE_ID")
    HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
    }

    query = """
    {
    viewer {
        zones(filter: { zoneTag: "%s" }) {
        httpRequests1dGroups(limit: 7, filter: { date_geq: "2025-04-12" }) {
            dimensions {
            date
            }
            sum {
            requests
            bytes
            cachedBytes
            encryptedBytes
            encryptedRequests
            }
            uniq {
            uniques
            }
        }
        }
    }
    }
    """ % ZONE_ID

    response = requests.post(
        "https://api.cloudflare.com/client/v4/graphql",
        headers=HEADERS,
        json={"query": query}
    )

    if response.status_code == 200:
        data = response.json()
        # Traitement des données selon tes besoins
        print(json.dumps(data, indent=2))
    else:
        print(f"Erreur : {response.status_code}")
        print(response.text)
