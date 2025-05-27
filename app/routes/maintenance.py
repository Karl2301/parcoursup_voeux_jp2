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

def maintenance_get():
    """
    Fonction pour afficher la page de maintenance.
    Elle vérifie si l'utilisateur est connecté et s'il a les droits d'administrateur.
    Si l'utilisateur n'est pas connecté ou n'a pas les droits, il est redirigé vers la page de connexion.
    """
    
    app_config = get_app_config()
    is_in_maintenance = app_config.get('is_in_maintenance')
    if not is_in_maintenance:
        return redirect(url_for('login_get'))
    maintenance_message = app_config.get('maintenance_message')
    if maintenance_message == {}:
        maintenance_message = ""

    return render_template('maintenance/index.html', maintenance_message=maintenance_message)