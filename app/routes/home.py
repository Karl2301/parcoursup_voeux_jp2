"""
Fonctions:
- home: Redirige l'utilisateur vers la page de connexion.
"""

from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
from flask_socketio import SocketIO, emit, join_room, leave_room


def home():
    return redirect(url_for('login_get'))
