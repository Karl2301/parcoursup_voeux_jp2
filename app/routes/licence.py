"""
Ce fichier définit les routes et les fonctionnalités liées à la gestion des licences 
dans l'application Flask. Il contient une fonction principale `licence` qui permet de :

- Vérifier l'existence du fichier de mentions légales.
- Lire et renvoyer le contenu du fichier de mentions légales sous forme de réponse HTML.
- Gérer les erreurs en cas d'absence du fichier de licence.

Ce fichier est essentiel pour afficher les informations légales obligatoires de l'application.
"""

import os
from flask import Flask, abort, Response, request
from ext_config import *
from ds import send_discord_message

def licence():
    app.logger.info("Client IP: %s", get_client_ip())
    app.logger.info("Licence check")
    # Construire le chemin absolu vers le fichier de licence
    base_dir = os.path.dirname(os.path.abspath(__file__))
    licence_path = os.path.join(base_dir, '..', 'protection_legale','mentions_legales.html')

    # Vérifier si le fichier existe
    if not os.path.exists(licence_path):
        abort(404)  # Retourner une erreur 404 si le fichier n'existe pas

    # Lire le contenu du fichier de licence
    with open(licence_path, 'r') as file:
        licence_content = file.read()


    # Renvoyer le contenu du fichier de licence
    send_discord_message("utilisateur_page_licence", "", get_url_from_request(request), get_client_ip())
    return Response(licence_content, mimetype='text/html')