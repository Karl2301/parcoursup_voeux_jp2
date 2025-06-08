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
    data = request.get_json()
    question = data.get('question', '')
    voeu = data.get('voeu', '')

    prompt = (
        f"Tu es un assistant expert Parcoursup. "
        f"Voici le vœu de l'élève : '{voeu}'. "
        f"Question de l'élève : '{question}'. "
        f"Réponds de façon concrète, claire, concise et utile pour un lycéen. Les élèves sont en terminale et ont besoin d'aide pour leurs vœux Parcoursup. Les réponses doivent être adaptées à leur niveau de compréhension et aux enjeux de Parcoursup. Les élèves sont à Rennes, donc propose une réponse localisé ou délocalisé selon le besoin. Tuoies l'utilisateur "
    )

    print(voeu)

    try:
        client = openai.OpenAI(api_key=openai.api_key)
        print(f"Clé API actuelle : {openai.api_key}")

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un assistant Parcoursup expert, très concret et clair. Si la question n'est pas liée à Parcoursup, réponds que tu ne peux pas aider."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.4
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        answer = f"Erreur lors de l'appel à l'IA : Cette fonctionnalité n'est pas encore totalement disponible pour cette année 2024-2025. Cependant elle sera disponible à la rentrée de septembre 2025 !"
        # answer = f"Erreur lors de l'appel à l'IA : {e}"

    return jsonify({'response': answer})





def ia_voeux_chat():
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
    question = data.get('question', '')
    voeu = data.get('voeu', '')
    history = data.get('history', [])

    # Construction de l'historique pour OpenAI
    messages = [
        {"role": "system", "content": (
            "Tu es un assistant Parcoursup expert, très concret et clair. "
            "Si la question n'est pas liée à Parcoursup, réponds que tu ne peux pas aider. "
            "Sois concis, utile, adapte-toi à un lycéen de terminale à Rennes. "
            "Tu est une IA d'une application Parcoursup, pour le Lycée Jean-Paul II a Saint-grégoire."
            "Tu est l'IA de l'application Voeux-JP2"
            "Si un utilisateur te demande quels sont les créateur de l'application, réponds que l'ensemble de l'application a été développé par 4 élèves du Lycée Jean-Paul II"
            "Les élèves ont deux tableaux sur leur page: un tableau pour les voeux que l'élèves veux vraiment, et l'autre tableau sert de corbeille pour les voeux que l'élèves ne souhaite pas vraiment ou moins que ceux dans le tableau principale. "
            "L'élèves n'a qu'a passer en mode édition pour pouvoir déplacer les voeux situé dans le tableau principale. Si il veux, il peut séléctionner des voeux d'un des tableaux et les déplacer dans l'autre tableau."
            "Pour chaques question, tu dois faire le discernement si la qustion porte sur l'application Voeux-JP2 ou sur Parcoursup."
            "Vœux multiples : Pour certaines formations, comme les BTS, BUT, CPGE, DCG, DN MADE, DNA, EFTS, vous pouvez formuler un vœu principal et ajouter jusqu'à 10 sous-vœux par établissement ou spécialité."
            "Sous-vœux limités : Le nombre total de sous-vœux est limité à 20."
            "Formations sans sous-vœux : Pour les IFSI, orthophonie, orthoptie, audioprothèse, écoles d'ingénieurs, écoles de commerce, Sciences Po, PASS en Île-de-France, et écoles vétérinaires, le nombre de sous-vœux n'est pas limité. "
            "Vous pouvez également formuler jusqu'à 10 vœux supplémentaires spécifiquement pour des formations en apprentissage, distincts des vœux principaux."
            "Si vous n'avez pas reçu de proposition en phase principale, la phase complémentaire vous permet de formuler jusqu'à 10 nouveaux vœux pour des formations ayant encore des places disponibles."
            f"Le vœu de l'élève : '{voeu}'."
        )}
    ]
    for msg in history:
        if msg.get('role') == 'user':
            messages.append({"role": "user", "content": msg.get('content', '')})
        elif msg.get('role') == 'ia':
            messages.append({"role": "assistant", "content": msg.get('content', '')})
    # Ajoute la question courante
    if question:
        messages.append({"role": "user", "content": question})

    try:
        client = openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=600,
            temperature=0.4
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        answer = f"Erreur lors de l'appel à l'IA : Cette fonctionnalité n'est pas encore totalement disponible pour cette année 2024-2025. Cependant elle sera disponible à la rentrée de septembre 2025 !"
        # answer = f"Erreur lors de l'appel à l'IA : {e}"

    return jsonify({'response': answer})