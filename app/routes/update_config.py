from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
import uuid
from flask_socketio import SocketIO, emit, join_room, leave_room
from ds import send_discord_message
import os

def update_config_post():
    """
    Fonction pour mettre à jour la configuration de l'application via un formulaire.
    Elle récupère les données du formulaire, les valide et met à jour le fichier de configuration JSON.
    """
    
    # Récupérer les données du formulaire
    data = request.get_json()
    flash("data", data)

    can_student_access = data.get('can_student_access')
    can_prof_access = data.get('can_prof_access')
    can_prof_reset_voeux = data.get('can_prof_reset_voeux')
    can_student_validate = data.get('can_student_validate')
    # Mettre à jour le fichier de configuration JSON

    # Construire le chemin absolu vers le fichier config.json
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../config.json')
    config_path = os.path.normpath(config_path)
    with open(config_path, 'w') as config_file:
        json.dump({
            'disable_student_access': can_student_access,
            'disable_prof_access': can_prof_access,
            'disable_prof_reset_voeux': can_prof_reset_voeux,
            'disable_student_validate': can_student_validate
        }, config_file, indent=4)
    
    # Vérifier que les informations ont été écrites correctement
    with open(config_path, 'r') as config_file:
        updated_config = json.load(config_file)
        if (updated_config.get('disable_student_access') == can_student_access and
            updated_config.get('disable_prof_access') == can_prof_access and
            updated_config.get('disable_prof_reset_voeux') == can_prof_reset_voeux and
            updated_config.get('disable_student_validate') == can_student_validate):
            flash("Configuration mise à jour et vérifiée avec succès.", "success")
        else:
            flash("Erreur lors de la vérification de la mise à jour de la configuration.", "error")
    return redirect(url_for('siteweb_get'))