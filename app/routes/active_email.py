from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
import uuid
from flask_socketio import SocketIO, emit, join_room, leave_room
from ds import send_discord_message

def post_want_email_on_all_validation():
    """
    Vérifie si l'utilisateur a activé la notification par e-mail pour la validation de tous les voeux.
    """
    session_cookie = request.cookies.get('session_cookie')
    data = request.get_json()
    email = data.get('email')
    active = data.get('active')

    if active:
        if not email:
            return jsonify({'error': 'Email is required'}), 400
    
    if not session_cookie:
        return jsonify({'error': 'No session cookie'}), 400
    
    with Session(engine) as session:
        user = get_user_by_cookie(session, session_cookie)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.professeur == False:
            return jsonify({'error': 'Not a professor'}), 403
        
        user.email = email
        user.want_email = active
        session.add(user)
        session.commit()

    return jsonify({'ok': True}), 200
        