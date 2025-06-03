import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, Response
import sqlmodel
from routes import *
from ext_config import *
from ext_config import maintenance_mode
from create_classes import create_all_classes
import requests
from flask import request, jsonify
from collections import defaultdict
import time
from flask import redirect, url_for
# from admin import admin test

create_all_classes()

app.add_url_rule('/', view_func=home, methods=['GET'])
app.add_url_rule('/login', view_func=login_get, methods=['GET'])
app.add_url_rule('/login', view_func=login_post, methods=['POST'])
app.add_url_rule('/dashboard', view_func=dashboard, methods=['GET'])
app.add_url_rule('/logout', view_func=logout, methods=['GET'])
app.add_url_rule('/get_data', view_func=get_data, methods=['GET'])
app.add_url_rule('/update_data', view_func=update_data, methods=['POST'])
app.add_url_rule('/settings', view_func=settings, methods=['GET'])
app.add_url_rule('/lost_id', view_func=lost_id_get, methods=['GET'])
app.add_url_rule('/lost_id', view_func=lost_id_post, methods=['POST'])
app.add_url_rule('/update-theme', view_func=update_theme, methods=['POST'])
app.add_url_rule('/get-theme', view_func=get_theme, methods=['GET'])
app.add_url_rule('/change_password', view_func=change_password_get, methods=['GET'])
app.add_url_rule('/change_password', view_func=change_password_post, methods=['POST'])
app.add_url_rule('/aide', view_func=aide_get, methods=['GET'])
app.add_url_rule('/aide', view_func=aide_post, methods=['POST'])
app.add_url_rule('/configure_password', view_func=configure_password_get, methods=['GET'])
app.add_url_rule('/configure_password', view_func=configure_password_post, methods=['POST'])
app.add_url_rule('/configure_prof', view_func=configure_prof_get, methods=['GET'])
app.add_url_rule('/configure_prof', view_func=configure_prof_post, methods=['POST'])
app.add_url_rule('/get_theme', view_func=get_theme, methods=['GET'])
app.add_url_rule('/classe/<class_name>', view_func=classes_prof_get, methods=['GET'])
app.add_url_rule('/get_voeux_status', view_func=get_voeux_status, methods=['GET'])
app.add_url_rule('/validate_voeux', view_func=post_voeux_status, methods=['POST'])
app.add_url_rule('/eleve/<eleve_id>', view_func=profil_eleve_get, methods=['GET'])
app.add_url_rule('/notifications', view_func=get_notifications, methods=['GET'])
app.add_url_rule('/upload_csv', view_func=upload_csv_get, methods=['GET'])
app.add_url_rule('/upload_csv', view_func=upload_csv, methods=['POST'])
app.add_url_rule('/download_voeux', view_func=download_voeux, methods=['GET'])
app.add_url_rule('/admin_dashboard', view_func=admin_dashboard, methods=['GET'])
app.add_url_rule('/delete_demande/<id>', view_func=delete_demande, methods=['DELETE'])
app.add_url_rule('/get_prof_data', view_func=get_prof_data, methods=['GET'])
app.add_url_rule('/save_prof_data', view_func=save_prof_data, methods=['POST'])
app.add_url_rule('/delete_prof', view_func=delete_prof, methods=['DELETE'])
app.add_url_rule('/status', view_func=status, methods=['GET'])
app.add_url_rule('/download_voeux_users_classe', view_func=download_voeux_users_classe, methods=['POST'])
app.add_url_rule('/set_deadline', view_func=deadline_post, methods=['POST'])
app.add_url_rule('/notif_voeux_invalide/<class_name>', view_func=notif_voeux_invalide, methods=['POST'])
app.add_url_rule('/reset_password/<identifiant>', view_func=reset_student_password, methods=['POST'])
app.add_url_rule('/licence', view_func=licence, methods=['GET'])
app.add_url_rule('/reset_voeux_validation', view_func=reset_voeux_validation_post, methods=['POST'])
app.add_url_rule('/didacticiel_get_state', view_func=didacticiel_get, methods=['GET'])
app.add_url_rule('/didacticiel_completed', view_func=didacticiel_post, methods=['POST'])
app.add_url_rule('/change_username', view_func=change_username_get, methods=['GET'])
app.add_url_rule('/change_username', view_func=change_username_post, methods=['POST'])
app.add_url_rule('/robots.txt', view_func=robot, methods=['GET'])
app.add_url_rule('/statistiques', view_func=statistiques_get, methods=['GET'])
app.add_url_rule('/get_statistiques', view_func=statistiques_get_data, methods=['GET'])
app.add_url_rule('/log', view_func=log_get, methods=['GET'])
app.add_url_rule('/siteweb', view_func=siteweb_get, methods=['GET'])
app.add_url_rule('/update_config', view_func=update_config_post, methods=['POST'])
app.add_url_rule('/admin_reset_password', view_func=admin_reset_password_post, methods=['POST'])
app.add_url_rule('/update_email_on_validation', view_func=post_want_email_on_all_validation, methods=['POST'])
app.add_url_rule('/log_fingerprint', view_func=log_fingerprint, methods=['POST'])
app.add_url_rule('/force_validate_voeux', view_func=force_validation, methods=['POST'])
app.add_url_rule('/maintenance', view_func=maintenance_get, methods=['GET'])

@app.before_request
def check_maintenance_mode():
    if request.headers.get('X-Forwarded-Proto', 'http') == 'http':
        return redirect(request.url.replace('http://', 'https://'), code=301)
        
    excluded_routes = ['maintenance_get', 'static']
    if request.method == 'GET':
        app_config = get_app_config()
        is_in_maintenance = app_config.get('is_in_maintenance')
        maintenance_level = app_config.get('maintenance_level', 'none')
        if is_in_maintenance and maintenance_level == 'extreme':
            endpoint = request.endpoint
            if endpoint not in excluded_routes:
                return redirect(url_for('maintenance_get'))

@app.after_request
def add_cache_headers(response: Response):
    """Ajoute des headers Cache-Control aux fichiers statiques (30 jours)."""
    if "Cache-Control" not in response.headers:
        response.headers["Cache-Control"] = "public, max-age=0, immutable"
    return response
    

def main():
    app.logger.info("Starting application...")
    app_port = int(APP_PORT)
    app.logger.info(f"App port: {app_port}")
    app.logger.info(f"version: {VERSION}")
    socketio.run(app, host="127.0.0.1", port=app_port, debug=True, use_reloader=True)

if __name__ == '__main__':
    main()
