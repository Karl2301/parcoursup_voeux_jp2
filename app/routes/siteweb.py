from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
import uuid
from flask_socketio import SocketIO, emit, join_room, leave_room
from ds import send_discord_message
from fonctions import get_user_by_cookie, get_client_ip, get_url_from_request, get_app_config

def siteweb_get():
    session_cookie = request.cookies.get('session_cookie')

    with Session(engine) as session:
        user = get_user_by_cookie(session, session_cookie)
        if not user:
            return redirect(url_for('login_get'))
        
        if not user.admin:
            return redirect(url_for('dashboard'))
        
        # Récupérer la configuration de l'application
        app_config = get_app_config()
        can_student_access = app_config.get('disable_student_access')
        can_prof_access = app_config.get('disable_prof_access')
        can_prof_reset_voeux = app_config.get('disable_prof_reset_voeux')
        can_student_validate = app_config.get('disable_student_validate')

        return render_template('siteweb/index.html', can_student_access=can_student_access, can_prof_access=can_prof_access, can_prof_reset_voeux=can_prof_reset_voeux, can_student_validate=can_student_validate, want_email=user.want_email, email=user.email)
    # return render_template('siteweb/index.html')