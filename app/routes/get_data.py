"""
Ce fichier, `get_data.py`, fait partie des routes de l'application Flask et gère la récupération 
des données utilisateur en fonction de leur rôle (élève, professeur ou administrateur). 

### Fonctionnalités principales :
1. **Gestion des cookies de session** :
    - Vérifie la présence et la validité d'un cookie de session pour identifier l'utilisateur.
    - Redirige vers la page de connexion si le cookie est absent ou invalide.

2. **Récupération des données utilisateur** :
    - Si l'utilisateur est un élève, retourne ses informations personnelles et son état (en ligne, choix validés, etc.).
    - Si l'utilisateur est un professeur, retourne des statistiques sur les élèves de ses classes (élèves en ligne, choix validés, etc.).
    - Si l'utilisateur est un administrateur, retourne des statistiques globales ainsi qu'une liste des professeurs.

3. **Gestion des rôles** :
    - Différencie les utilisateurs en fonction de leur rôle (élève, professeur, administrateur) et adapte les données retournées.

4. **Statistiques et données spécifiques** :
    - Compte les élèves en ligne, les choix validés, les demandes d'aide, et les classes associées.
    - Fournit une liste des professeurs avec leurs informations et classes associées.

Ce fichier est essentiel pour fournir des données dynamiques et adaptées à chaque utilisateur connecté, 
en fonction de son rôle et de ses permissions.
"""

from flask import Flask, request, redirect, url_for, jsonify
from sqlmodel import Session, select
from ext_config import *
import json
import logging

def get_data():
    session_cookie = request.cookies.get('session_cookie')
    if not session_cookie:
        return redirect(url_for('login_get'))

    with Session(engine) as session:
        user = get_user_by_cookie(session, session_cookie)
        if not user:
            return redirect(url_for('login_get'))

        if not user.professeur:  # C'est un élève
            return jsonify({
                'identifiant_unique': user.identifiant_unique,
                'cookie': user.cookie,
                'niveau_classe': user.niveau_classe,
                'voeux_etablissements': user.voeux_etablissements,
                'online': user.online,
                'deja_connecte': user.deja_connecte,
                'choix_validees': user.choix_validees,
                'professeur': user.professeur,
                'status_class': 'status.delivered' if user.online else 'status.offline',
                'didacticiel': user.didacticiel
            })

        # C'est un professeur
        niveau_classe = json.loads(user.niveau_classe)
        eleve_online_count = session.exec(select(Users).where(Users.online == True, Users.niveau_classe.in_(niveau_classe))).all()
        eleve_choix_validees_count = session.exec(select(Users).where(Users.choix_validees == True, Users.niveau_classe.in_(niveau_classe))).all()
        demande_aide_count = session.exec(select(DemandeAide).where(DemandeAide.classe.in_(niveau_classe))).all()
        liste_prof = session.exec(select(Superieurs).where((Superieurs.professeur == True) & (Superieurs.admin == False))).all()
        liste_prof_json = [{'identifiant_unique': prof.identifiant_unique, 'nom': prof.nom, 'prenom': prof.prenom, 'classes': json.loads(prof.niveau_classe)} for prof in liste_prof]

        niveau_classe_list = niveau_classe

        if user.admin == True: # C'est un admin
            return jsonify({
                'identifiant_unique': user.identifiant_unique,
                'cookie': user.cookie,
                'niveau_classe': user.niveau_classe,
                'online': user.online,
                'deja_connecte': user.deja_connecte,
                'professeur': user.professeur,
                'admin': user.admin,
                'eleve_online': len(eleve_online_count),
                'eleve_choix_validees': len(eleve_choix_validees_count),
                'identifiant_perdus': len(demande_aide_count),
                'classes': len(niveau_classe_list),
                'liste_prof': liste_prof_json,
                'status_class': 'status.delivered' if user.online else 'status.offline',
                'want_email': user.want_email,
                'email': user.email
            })
        else: # C'est un prof
            return jsonify({
                'identifiant_unique': user.identifiant_unique,
                'cookie': user.cookie,
                'niveau_classe': user.niveau_classe,
                'online': user.online,
                'deja_connecte': user.deja_connecte,
                'professeur': user.professeur,
                'admin': user.admin,
                'eleve_online': len(eleve_online_count),
                'eleve_choix_validees': len(eleve_choix_validees_count),
                'identifiant_perdus': len(demande_aide_count),
                'classes': len(niveau_classe_list),
                'status_class': 'status.delivered' if user.online else 'status.offline',
                'want_email': user.want_email,
                'email': user.email
            })

