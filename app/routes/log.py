from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
from flask_socketio import SocketIO, emit, join_room, leave_room
import logging

def log_get():
    session_cookie = request.cookies.get('session_cookie')

    if not session_cookie:
        return redirect(url_for('login_get'))
    
    with Session(engine) as session:
        user = get_user_by_cookie(session, session_cookie)
        if not user:
            return redirect(url_for('login_get'))
        if not user.admin:
            return redirect(url_for('home'))

    return render_template('log/index.html')


@socketio.on('new_log')
def handle_new_log(data):
    emit('new_log', data, broadcast=True)