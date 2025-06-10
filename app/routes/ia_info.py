import openai
import os
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
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Random import get_random_bytes
from Crypto import Random


def ia_voeux():
    """
    Endpoint pour le chatbot IA avec historique de conversation.
    Attend : {
        "question": "...",
        "voeu": "...",
        "history": [
            {"role": "user"|"ia", "content": "..."},
            ...
        ]
    }
    """
    data = request.get_json()
    question_text = data.get('question', '').strip()
    voeu = data.get('voeu', '').strip()
    print(voeu)
    history = data.get('history', [])

    # Construction du prompt système (avec espaces entre phrases)
    system_prompt = (
        "Tu es un assistant Parcoursup expert, très concret et clair. "
        "Si la question n'est pas liée au vaste domaine éducatif ou orientation professionel, réponds que tu ne peux pas aider. "
        "Si un utilisateur te demande une question ou fait un lien avec une question de l'historique de la conversation, reponds lui en prenant en compte l'historique"
        "Sois concis, utile, adapte-toi à un lycéen de terminale à Rennes. "
        "Tu es une IA d'une application Parcoursup, pour le Lycée Jean-Paul II à Saint-Grégoire. "
        "Tu es l'IA de l'application Voeux-JP2. "
        "Si un utilisateur te demande quels sont les créateurs de l'application, réponds que l'ensemble de l'application a été développé par 4 élèves du Lycée Jean-Paul II. "
        "Les élèves ont deux tableaux sur leur page : un tableau pour les vœux que l'élève souhaite absolument, et l'autre tableau sert de corbeille pour les vœux moins souhaités. "
        "L'élève peut passer en mode édition pour déplacer les vœux entre ces tableaux. "
        "Pour chaque question, fais le discernement si elle porte sur l'application Voeux-JP2 ou sur Parcoursup. "
        "Vœux multiples : certaines formations comme BTS, BUT, CPGE, DCG, DN MADE, DNA, EFTS permettent un vœu principal et jusqu'à 10 sous-vœux par établissement ou spécialité. "
        "Le nombre total de sous-vœux est limité à 20. "
        "Pour les formations sans sous-vœux (IFSI, orthophonie, écoles d'ingénieurs, etc.), il n'y a pas de limite. "
        "Vous pouvez formuler jusqu'à 10 vœux supplémentaires pour des formations en apprentissage distincts des vœux principaux. "
        "Si vous n'avez pas reçu de proposition en phase principale, la phase complémentaire permet de formuler jusqu'à 10 nouveaux vœux pour des formations avec places disponibles. "
        "L'application n'a aucune influence et n'est pas liée au site Parcoursup, c'est seulement un outils pour le lycée."
        "Utilise le Markdown pour embellire tes réponses"
    )

    # Construction des messages
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        role = msg.get('role')
        if role == 'user':
            messages.append({"role": "user", "content": msg.get('content', '')})
        elif role == 'ia':
            messages.append({"role": "assistant", "content": msg.get('content', '')})

    prompt = f"""
Le vœu de l'élève qui sert a répondre a la question: '{voeu}'.
Question: {question_text}
"""
    
    # Ajout de la question courante
    messages.append({"role": "user", "content": prompt})


    try:
        client = openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=messages,
            max_tokens=800,
            temperature=0.9
        )
        answer_raw = response.choices[0].message.content.strip()

        # Retourne la réponse complète avec info booléenne séparée
        return jsonify({
            'response': answer_raw
        })

    except Exception as e:
        return jsonify({
            'response': ("Erreur lors de l'appel à l'IA : Cette fonctionnalité n'est pas encore totalement disponible "
                         "pour cette année 2024-2025. Cependant elle sera disponible à la rentrée de septembre 2025 !"),
            'needs_context': None
        })
