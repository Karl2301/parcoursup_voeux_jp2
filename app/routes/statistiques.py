from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
import uuid
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime, timedelta

def statistiques_get():
    """
    Affiche la page des statistiques.
    Vérifie si l'utilisateur est connecté et redirige vers la page de connexion si ce n'est pas le cas.
    """

    session_cookie = request.cookies.get('session_cookie')
    if session_cookie == None:
        return redirect(url_for('login_get'))

    with Session(engine) as session:
        user = get_user_by_cookie(session, session_cookie)
        if not user:
            return redirect(url_for('login_get'))
        if not user.admin:
            return redirect(url_for('home'))
                
    return render_template('statistiques/index.html')



def statistiques_get_data():
    """
    Récupère toutes les statistiques et les renvoie sous forme de JSON structuré.
    """
    filter_type = request.args.get('filter_type', 'all')  # Récupérer le paramètre depuis la requête
    session_cookie = request.cookies.get('session_cookie')
    if not session_cookie:
        return jsonify({'error': 'No session cookie'}), 400
    with Session(engine) as session:
        user = get_user_by_cookie(session, session_cookie)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        if not user.professeur and not user.admin:
            return jsonify({'error': 'User not authorized'}), 403

        try:
            # Appeler les fonctions existantes pour récupérer les données
            voeux_total_par_classe = statistiques_get_voeux_total_par_classe(filter_type).json.get("voeux_total_par_classe", {})
            moyenne_voeux_par_eleve_par_classe = statistiques_get_moyenne_voeux_par_classe(filter_type).json.get("moyenne_voeux_par_eleve_par_classe", {})
            voeux_par_type_par_classe = statistiques_get_voeux_par_type_par_classe(filter_type).json.get("top_voeux_par_type_par_classe", {})
            repartition_voeux_par_ville = statistiques_get_top_villes_par_voeux(filter_type).json.get("repartition_voeux_par_ville", {})
            top_10_formations = statistiques_get_top_formations(filter_type).json.get("top_10_formations", [])
            repartition_types_formation = statistiques_get_repartition_types_formation(filter_type).json.get("repartition_types_formation", {})
            voeux_par_etablissement = statistiques_get_voeux_par_etablissement(filter_type).json.get("top_etablissements", {})
            eleves_par_formation = statistiques_get_eleves_par_formation(filter_type).json.get("top_eleves_par_formation", {})
            voeux_par_semaine = statistiques_get_voeux_par_semaine().json.get("voeux_par_semaine", {})

            # Structurer les données dans le format demandé
            statistiques = {
                "statistiques": {
                    "voeux_total_par_classe": voeux_total_par_classe,
                    "moyenne_voeux_par_eleve_par_classe": moyenne_voeux_par_eleve_par_classe,
                    "voeux_par_type_par_classe": voeux_par_type_par_classe,
                    "repartition_voeux_par_ville": repartition_voeux_par_ville,
                    "top_10_formations": top_10_formations,
                    "repartition_types_formation": repartition_types_formation,
                    "voeux_par_etablissement": voeux_par_etablissement,
                    "eleves_par_formation": eleves_par_formation,
                    "voeux_par_semaine": voeux_par_semaine
                }
            }

            # Retourner les données sous forme de JSON
            return jsonify(statistiques), 200

        except Exception as e:
            abort(500, description="Erreur interne du serveur")



def statistiques_get_voeux_total_par_classe(filter_type="all"):
    """
    Récupère le nombre total de vœux par classe en fonction du filtre.
    Renvoie les données au format JSON.
    """
    try:
        voeux_total_par_classe = {}

        with Session(engine) as session:
            # Récupérer toutes les classes et leurs vœux
            results = session.exec(select(Users.niveau_classe, Users.voeux_etablissements)).all()

            for niveau_classe, voeux_etablissements in results:
                if niveau_classe not in voeux_total_par_classe:
                    voeux_total_par_classe[niveau_classe] = 0

                # Convertir la chaîne de caractères en liste Python
                if voeux_etablissements:
                    voeux_list = json.loads(voeux_etablissements)

                    # Filtrer les vœux en fonction de filter_type
                    if filter_type == "classed":
                        voeux_list = [voeu for voeu in voeux_list if voeu.get("enable") is True]
                    elif filter_type == "unclassed":
                        voeux_list = [voeu for voeu in voeux_list if voeu.get("enable") is False]

                    voeux_total_par_classe[niveau_classe] += len(voeux_list)
        return jsonify({"voeux_total_par_classe": voeux_total_par_classe})

    except Exception as e:
        abort(500, description="Erreur interne du serveur")


def statistiques_get_moyenne_voeux_par_classe(filter_type="all"):
    """
    Récupère la moyenne des vœux par élève pour chaque classe en fonction du filtre.
    Renvoie les données au format JSON.
    """
    try:
        voeux_total_par_classe = {}
        eleves_par_classe = {}
        moyenne_voeux_par_eleve_par_classe = {}

        with Session(engine) as session:
            # Récupérer toutes les classes et leurs vœux
            results = session.exec(select(Users.niveau_classe, Users.voeux_etablissements)).all()

            for niveau_classe, voeux_etablissements in results:
                if niveau_classe not in voeux_total_par_classe:
                    voeux_total_par_classe[niveau_classe] = 0
                    eleves_par_classe[niveau_classe] = 0

                # Compter l'élève dans la classe
                eleves_par_classe[niveau_classe] += 1

                # Convertir la chaîne de caractères en liste Python
                if voeux_etablissements:
                    voeux_list = json.loads(voeux_etablissements)

                    # Filtrer les vœux en fonction de filter_type
                    if filter_type == "classed":
                        voeux_list = [voeu for voeu in voeux_list if voeu.get("enable") is True]
                    elif filter_type == "unclassed":
                        voeux_list = [voeu for voeu in voeux_list if voeu.get("enable") is False]

                    voeux_total_par_classe[niveau_classe] += len(voeux_list)

            # Calculer la moyenne des vœux par élève pour chaque classe
            for classe, total_voeux in voeux_total_par_classe.items():
                if eleves_par_classe[classe] > 0:
                    moyenne_voeux_par_eleve_par_classe[classe] = round(total_voeux / eleves_par_classe[classe], 2)
                else:
                    moyenne_voeux_par_eleve_par_classe[classe] = 0.0
        return jsonify({"moyenne_voeux_par_eleve_par_classe": moyenne_voeux_par_eleve_par_classe})

    except Exception as e:
        abort(500, description="Erreur interne du serveur")


def statistiques_get_voeux_par_type_par_classe(filter_type="all"):
    """
    Récupère les 5 types de voie les plus fréquents par classe en fonction du filtre.
    Renvoie les données au format JSON.
    """
    try:
        voeux_par_type_par_classe = {}

        with Session(engine) as session:
            # Récupérer toutes les classes et leurs vœux
            results = session.exec(select(Users.niveau_classe, Users.voeux_etablissements)).all()

            for niveau_classe, voeux_etablissements in results:
                if niveau_classe not in voeux_par_type_par_classe:
                    voeux_par_type_par_classe[niveau_classe] = {}

                # Convertir la chaîne de caractères en liste Python
                if voeux_etablissements:
                    voeux_list = json.loads(voeux_etablissements)

                    # Filtrer les vœux en fonction de filter_type
                    if filter_type == "classed":
                        voeux_list = [voeu for voeu in voeux_list if voeu.get("enable") is True]
                    elif filter_type == "unclassed":
                        voeux_list = [voeu for voeu in voeux_list if voeu.get("enable") is False]

                    # Compter les types de voie
                    for voeu in voeux_list:
                        voie_type = voeu.get("degree")  # Exemple : "BUT", "BTS", etc.
                        if voie_type:
                            if voie_type not in voeux_par_type_par_classe[niveau_classe]:
                                voeux_par_type_par_classe[niveau_classe][voie_type] = 0
                            voeux_par_type_par_classe[niveau_classe][voie_type] += 1

            # Limiter à 5 types de voie les plus fréquents par classe
            top_voeux_par_type_par_classe = {}
            for classe, voies in voeux_par_type_par_classe.items():
                # Trier les types de voie par ordre décroissant de leur nombre
                sorted_voies = sorted(voies.items(), key=lambda x: x[1], reverse=True)
                # Garder les 5 premiers
                top_voies = dict(sorted_voies[:6])
                top_voeux_par_type_par_classe[classe] = top_voies

        return jsonify({"top_voeux_par_type_par_classe": top_voeux_par_type_par_classe})

    except Exception as e:
        abort(500, description="Erreur  du serveur")


def statistiques_get_top_villes_par_voeux(filter_type="all"):
    """
    Récupère le top 10 des villes les plus demandées dans les vœux de toutes les classes.
    Renvoie les données au format JSON.
    """
    try:
        voeux_par_ville = {}

        with Session(engine) as session:
            # Récupérer toutes les classes et leurs vœux
            results = session.exec(select(Users.voeux_etablissements)).all()

            for result in results:
                voeux_etablissements = result  # Accéder directement à la colonne

                # Convertir la chaîne de caractères en liste Python
                if voeux_etablissements:
                    voeux_list = json.loads(voeux_etablissements)

                    # Filtrer les vœux en fonction de filter_type
                    if filter_type == "classed":
                        voeux_list = [voeu for voeu in voeux_list if voeu.get("enable") is True]
                    elif filter_type == "unclassed":
                        voeux_list = [voeu for voeu in voeux_list if voeu.get("enable") is False]

                    # Compter les villes
                    for voeu in voeux_list:
                        ville = voeu.get("city")  # Exemple : "Brest", "Rennes", etc.
                        if ville:
                            # Normaliser le nom de la ville (minuscule + première lettre en majuscule)
                            ville_normalisee = ville.strip().lower().title()
                            if ville_normalisee not in voeux_par_ville:
                                voeux_par_ville[ville_normalisee] = 0
                            voeux_par_ville[ville_normalisee] += 1

            # Trier les villes par ordre décroissant de leur nombre de vœux
            sorted_villes = sorted(voeux_par_ville.items(), key=lambda x: x[1], reverse=True)
            # Garder les 10 premières villes
            top_villes = dict(sorted_villes[:10])

        return jsonify({"repartition_voeux_par_ville": top_villes})

    except Exception as e:
        abort(500, description="Erreur interne du serveur")


def statistiques_get_top_formations(filter_type="all"):
    """
    Récupère les 10 formations les plus demandées dans les vœux de toutes les classes.
    Renvoie les données au format JSON.
    """
    try:
        voeux_par_formation = {}

        with Session(engine) as session:
            # Récupérer toutes les classes et leurs vœux
            results = session.exec(select(Users.voeux_etablissements)).all()

            for result in results:
                voeux_etablissements = result  # Accéder directement à la colonne

                # Convertir la chaîne de caractères en liste Python
                if voeux_etablissements:
                    voeux_list = json.loads(voeux_etablissements)

                    # Filtrer les vœux en fonction de filter_type
                    if filter_type == "classed":
                        voeux_list = [voeu for voeu in voeux_list if voeu.get("enable") is True]
                    elif filter_type == "unclassed":
                        voeux_list = [voeu for voeu in voeux_list if voeu.get("enable") is False]

                    # Compter les formations
                    for voeu in voeux_list:
                        formation = voeu.get("specialization")  # Exemple : "BUT GEA Brest", "BTS NDRC Quimper", etc.
                        if formation:
                            if formation not in voeux_par_formation:
                                voeux_par_formation[formation] = 0
                            voeux_par_formation[formation] += 1

            # Trier les formations par ordre décroissant de leur nombre de vœux
            sorted_formations = sorted(voeux_par_formation.items(), key=lambda x: x[1], reverse=True)
            # Garder les 10 premières formations
            top_formations = [{"nom": formation, "count": count} for formation, count in sorted_formations[:10]]

        return jsonify({"top_10_formations": top_formations})

    except Exception as e:
        abort(500, description="Erreur interne du serveur")


def statistiques_get_repartition_types_formation(filter_type="all"):
    """
    Récupère la répartition des 10 types de formation les plus fréquents dans les vœux de toutes les classes.
    Renvoie les données au format JSON.
    """
    try:
        types_formation = {}

        with Session(engine) as session:
            # Récupérer toutes les classes et leurs vœux
            results = session.exec(select(Users.voeux_etablissements)).all()

            for result in results:
                voeux_etablissements = result  # Accéder directement à la colonne

                # Convertir la chaîne de caractères en liste Python
                if voeux_etablissements:
                    voeux_list = json.loads(voeux_etablissements)

                    # Filtrer les vœux en fonction de filter_type
                    if filter_type == "classed":
                        voeux_list = [voeu for voeu in voeux_list if voeu.get("enable") is True]
                    elif filter_type == "unclassed":
                        voeux_list = [voeu for voeu in voeux_list if voeu.get("enable") is False]

                    # Compter les types de formation
                    for voeu in voeux_list:
                        type_formation = voeu.get("degree")  # Exemple : "BUT", "BTS", etc.
                        if type_formation:
                            if type_formation not in types_formation:
                                types_formation[type_formation] = 0
                            types_formation[type_formation] += 1

        # Trier les types de formation par ordre décroissant de leur nombre
        sorted_types = sorted(types_formation.items(), key=lambda x: x[1], reverse=True)

        # Garder uniquement les 10 premiers types de formation
        top_10_types_formation = dict(sorted_types[:10])

        return jsonify({"repartition_types_formation": top_10_types_formation})

    except Exception as e:
        abort(500, description="Erreur interne du serveur")

def statistiques_get_voeux_par_etablissement(filter_type="all"):
    """
    Récupère les 20 établissements les plus demandés dans les vœux de toutes les classes.
    Renvoie les données au format JSON.
    """
    try:
        voeux_par_etablissement = {}

        with Session(engine) as session:
            # Récupérer toutes les classes et leurs vœux
            results = session.exec(select(Users.voeux_etablissements)).all()

            for result in results:
                voeux_etablissements = result  # Accéder directement à la colonne

                # Convertir la chaîne de caractères en liste Python
                if voeux_etablissements:
                    voeux_list = json.loads(voeux_etablissements)

                    # Filtrer les vœux en fonction de filter_type
                    if filter_type == "classed":
                        voeux_list = [voeu for voeu in voeux_list if voeu.get("enable") is True]
                    elif filter_type == "unclassed":
                        voeux_list = [voeu for voeu in voeux_list if voeu.get("enable") is False]

                    # Compter les établissements
                    for voeu in voeux_list:
                        etablissement = voeu.get("school")  # Exemple : "I.U.T de Brest", "Lycée Dupuy de Lôme", etc.
                        if etablissement:
                            if etablissement not in voeux_par_etablissement:
                                voeux_par_etablissement[etablissement] = 0
                            voeux_par_etablissement[etablissement] += 1

            # Trier les établissements par ordre décroissant de leur nombre de vœux
            sorted_etablissements = sorted(voeux_par_etablissement.items(), key=lambda x: x[1], reverse=True)
            # Garder les 20 premiers établissements
            top_etablissements = dict(sorted_etablissements[:10])

        return jsonify({"top_etablissements": top_etablissements})

    except Exception as e:
        abort(500, description="Erreur interne du serveur")


def statistiques_get_eleves_par_formation(filter_type="all"):
    """
    Récupère les 20 formations les plus demandées en termes de nombre d'élèves.
    Renvoie les données au format JSON.
    """
    try:
        eleves_par_formation = {}

        with Session(engine) as session:
            # Récupérer toutes les classes et leurs vœux
            results = session.exec(select(Users.voeux_etablissements)).all()

            for result in results:
                voeux_etablissements = result  # Accéder directement à la colonne

                # Convertir la chaîne de caractères en liste Python
                if voeux_etablissements:
                    voeux_list = json.loads(voeux_etablissements)

                    # Filtrer les vœux en fonction de filter_type
                    if filter_type == "classed":
                        voeux_list = [voeu for voeu in voeux_list if voeu.get("enable") is True]
                    elif filter_type == "unclassed":
                        voeux_list = [voeu for voeu in voeux_list if voeu.get("enable") is False]

                    # Utiliser un set pour éviter les doublons d'élèves par formation
                    formations_par_eleve = set()

                    for voeu in voeux_list:
                        formation = voeu.get("specialization")  # Exemple : "BUT GEA Brest", "BTS NDRC Quimper", etc.
                        if formation:
                            formations_par_eleve.add(formation)

                    # Incrémenter le compteur pour chaque formation unique
                    for formation in formations_par_eleve:
                        if formation not in eleves_par_formation:
                            eleves_par_formation[formation] = 0
                        eleves_par_formation[formation] += 1

            # Trier les formations par ordre décroissant du nombre d'élèves
            sorted_formations = sorted(eleves_par_formation.items(), key=lambda x: x[1], reverse=True)
            # Garder les 20 premières formations
            top_formations = dict(sorted_formations[:10])

        return jsonify({"top_eleves_par_formation": top_formations})

    except Exception as e:
        abort(500, description="Erreur interne du serveur")


from datetime import datetime

def statistiques_get_voeux_par_semaine():
    """
    Récupère le nombre de vœux validés par semaine.
    Renvoie les données au format JSON.
    """
    try:
        voeux_par_semaine = {}

        with Session(engine) as session:
            # Récupérer toutes les dates de validation des vœux
            results = session.exec(select(Users.voeux_validation)).all()

            # Filtrer les utilisateurs ayant une date de validation
            dates_validation = [result for result in results if result is not None]

            if not dates_validation:
                return jsonify({"voeux_par_semaine": {}})  # Aucun vœu validé

            # Calculer les semaines ISO
            for date_validation in dates_validation:
                # Obtenir le numéro de semaine ISO
                semaine = date_validation.isocalendar()[1]  # [1] correspond au numéro de semaine
                semaine_label = f"Semaine {semaine}"

                if semaine_label not in voeux_par_semaine:
                    voeux_par_semaine[semaine_label] = 0
                voeux_par_semaine[semaine_label] += 1

        return jsonify({"voeux_par_semaine": voeux_par_semaine})

    except Exception as e:
        abort(500, description="Erreur interne du serveur")