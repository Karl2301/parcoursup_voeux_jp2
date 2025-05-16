"""
Ce fichier contient la fonction `update_data` qui est utilisée pour mettre à jour les données des étudiants dans la base de données.

Fonctionnalités :
- Vérifie l'existence d'un cookie de session pour identifier l'utilisateur.
- Récupère les données mises à jour envoyées dans la requête JSON.
- Met à jour les voeux des établissements de l'utilisateur dans la base de données.
- Gère les erreurs potentielles et effectue un rollback en cas d'échec de la mise à jour.

Ce fichier est utilisé lorsque l'utilisateur souhaite mettre à jour ses voeux d'établissements via une requête HTTP.
"""

from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
from flask_socketio import SocketIO, emit, join_room, leave_room



def update_data():
    session_cookie = request.cookies.get('session_cookie')
    app.logger.info("Client IP: %s", get_client_ip())
    app.logger.info("Session cookie: %s", session_cookie)
    if session_cookie:
        with Session(engine) as session:
            user= get_user_by_cookie(session, session_cookie)
            if user:
                try:
                    # Retrieve the current data stored in the server
                    current_data = json.loads(user.voeux_etablissements)

                    # Normalize the data by removing 'row_number' and 'enable' keys
                    def normalize_data(data):
                        return [{k: v for k, v in item.items() if k not in ['row_number', 'enable']} for item in data]

                    normalized_current_data = normalize_data(current_data)
                    normalized_updated_data = normalize_data(request.json)

                    # Check if all elements in the current data exist in the updated data
                    if not all(item in normalized_updated_data for item in normalized_current_data):
                        app.logger.warning("Data mismatch detected. Update aborted.")
                        return jsonify({'success': False, 'message': 'Data mismatch detected. Update aborted.'})
                    
                    updated_data = request.json
                    user.voeux_etablissements = json.dumps(updated_data)
                    # user.voeux_etablissements = str(updated_data).replace("'", '"')
                    session.add(user)
                    session.commit()
                    app.logger.info("User data updated successfully for user: %s", user.identifiant_unique)
                    return jsonify({'success': True})
                except Exception as e:
                    session.rollback()
                    return jsonify({'success': False, 'message': str(e)})
            else:
                return redirect(url_for('login_get'))
    return jsonify({'success': False, 'message': 'No session cookie found'})
