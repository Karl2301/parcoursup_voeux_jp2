from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import current_app

def notif_voeux_invalide(class_name):
    session_cookie = request.cookies.get('session_cookie')
    if not session_cookie:
        return jsonify({'success': False, 'error': 'Session cookie missing'}), 401
    
    with Session(engine) as session:
        # Récupérer le professeur connecté à partir du cookie de session
        teacher = session.exec(select(Superieurs).where(Superieurs.cookie == session_cookie)).one_or_none()
        if not teacher:
            return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
        # Vérifier que le professeur a accès à la classe
        prof_classes = json.loads(teacher.niveau_classe)
        if class_name not in prof_classes:
            return jsonify({'success': False, 'error': "Vous n'avez pas accès à cette classe"}), 403
        
        # Récupérer les élèves de la classe qui n'ont pas validé leurs vœux
        students = session.exec(
            select(Users).where(
                (Users.niveau_classe == class_name) &
                (Users.professeur == 0) &
                ((Users.choix_validees == None) | (Users.choix_validees == False))
            )
        ).all()
        
        # Message de notification
        message = "Veuillez valider vos vœux avant la date limite."
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Pour chaque élève non validé, créer une notification
        for student in students:
            notif = NotificationsVoeux(
                identifiant_eleve=student.identifiant_unique,
                message=message,
                created_at=now_str
            )
            session.add(notif)
        session.commit()
        
        # Retourner une réponse JSON indiquant le succès
        return jsonify({'success': True, 'message': "Notification envoyée aux élèves non validés."})