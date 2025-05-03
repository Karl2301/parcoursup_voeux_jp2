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
from collections import defaultdict
import time


FINGERPRINT_COUNTS = defaultdict(list)
BLOCKED_FINGERPRINTS = {}

def log_fingerprint():
    data = request.get_json()
    fingerprint = data.get("fingerprint")
    print("Fingerprint:", fingerprint)

    if not fingerprint:
        return jsonify({"error": "No fingerprint provided"}), 400

    current_time = time.time()

    if fingerprint in BLOCKED_FINGERPRINTS:
        if current_time < BLOCKED_FINGERPRINTS[fingerprint]:
            return jsonify({"error": "Too many requests. Blocked"}), 403
        else:
            del BLOCKED_FINGERPRINTS[fingerprint]

    FINGERPRINT_COUNTS[fingerprint].append(current_time)

    # Garder les requêtes des 10 dernières secondes
    FINGERPRINT_COUNTS[fingerprint] = [
        t for t in FINGERPRINT_COUNTS[fingerprint] if current_time - t <= 1
    ]

    if len(FINGERPRINT_COUNTS[fingerprint]) > 1:
        BLOCKED_FINGERPRINTS[fingerprint] = current_time + 300
        return jsonify({"error": "Too many requests. Blocked"}), 403

    return jsonify({"status": "ok"})
