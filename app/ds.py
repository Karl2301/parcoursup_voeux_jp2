import requests
import urllib3
from datetime import datetime, timezone
from pytz import timezone
from ext_config import socketio, DISCORD_WEBHOOK_URL

# Masquer les avertissements InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

WEBHOOK_URL = f"https://discord.com/api/webhooks/1374374006173733036/{DISCORD_WEBHOOK_URL}"

def send_discord_message(etat_message: str, user_id: str, provenance: str = "", ip: str = "??.??.??.??"):
    """Envoie un message à un webhook Discord de manière synchrone"""

    etats_messages = {
        "login_success": f"✅ L'utilisateur `{user_id}` s'est connecté avec succès.",
        "creation_compte_prof": f"🆕 Un compte **professeur** a été créé pour `{user_id}`.",
        "compte_prof_supprime": f"🗑️ Le compte **professeur** `{user_id}` a été supprimé.",
        "voeux_valides": f"🎯 Les vœux de `{user_id}` ont été validés.",
        "demande_aide": f"🆘 `{user_id}` a envoyé une demande d'aide.",
        "didacticiel_termine": f"📚 `{user_id}` a terminé le didacticiel.",
        "prof_telecharge_pdf_xlsx": f"📂 Un **professeur** (`{user_id}`) a téléchargé un fichier PDF/XLSX.",
        "eleve_telecharge_pdf_xlsx": f"📂 Un **élève** (`{user_id}`) a téléchargé un fichier PDF/XLSX.",
        "utilisateur_page_licence": f"ℹ️ Un utilisateur est actuellement sur la page **Licence**.",
        "utilisateur_deconnecte": f"🔒 L'utilisateur `{user_id}` s'est déconnecté.",
        "all_voeux_valides": f"✅ Tous les élèves ont validé leurs vœux.",
    }

    color_messages = { 
        "login_success": 0x00FF00,  # Vert
        "creation_compte_prof": 0xFFFF00,  # Jaune
        "compte_prof_supprime": 0xFF0000,  # Rouge
        "voeux_valides": 0x00FF00,  # Vert
        "demande_aide": 0xFFA500,  # Orange
        "didacticiel_termine": 0x0000FF,  # Bleu
        "prof_telecharge_pdf_xlsx": 0xFFA500,  # Orange
        "eleve_telecharge_pdf_xlsx": 0xFFA500,  # Orange
        "utilisateur_page_licence": 0x808080,  # Gris
        "utilisateur_deconnecte": 0xFF0000,  # Rouge
        "all_voeux_valides": 0xFFFFFF,  # Blanc
    }

    etat_html_color = {
        "login_success": "success",  # Vert
        "creation_compte_prof": "warning",  # Jaune
        "compte_prof_supprime": "error",  # Rouge
        "voeux_valides": "success",  # Vert
        "demande_aide": "bad",  # Orange
        "didacticiel_termine": "info",  # Bleu
        "prof_telecharge_pdf_xlsx": "bad",  # Orange
        "eleve_telecharge_pdf_xlsx": "bad",  # Orange
        "utilisateur_page_licence": "msg",  # Gris
        "utilisateur_deconnecte": "error",  # Rouge
        "all_voeux_valides": "success",  # Vert
    }
    # Vérification de l'état du message

    message_final = etats_messages.get(etat_message, f"ℹ️ `{user_id}` : Événement inconnu.")
    paris_timezone = timezone('Europe/Paris')
    heure = datetime.now(paris_timezone).strftime("%H:%M:%S")

    payload  =  {
        "embeds": [
            {
                "title": f"Événement" if user_id == "" else f"Événement ( **{user_id}** )",
                "description": message_final,
                "color": color_messages.get(etat_message),  # Couleur verte
                "footer": {
                    #"text": f"Provenance : {provenance} \nIP : {ip}" if user_id == "" else f"Utilisateur : {user_id}\nProvenance : {provenance} \nIP : {ip}",
                    "text": f"Provenance : {provenance} \nHeure: {heure}" if user_id == "" else f"Utilisateur : {user_id}\nProvenance : {provenance} \nHeure: {heure}",
                    "icon_url": "https://www.voeux-jp2.fr/static/img/whiteBgColor.png"  # URL de l'icône du pied de page
                }
            }
        ]
    }

    try:
        response = requests.post(WEBHOOK_URL, json=payload, verify=False)

        if response.status_code != 204:
            print(f"❌ Erreur {response.status_code}: {response.text}")

        log_data = {
            "etat": etat_html_color.get(etat_message),
            "user_id": user_id,
            "description": message_final,
            "time": heure,
            "title": f"Événement" if user_id == "" else f"Événement ({user_id})",
            "provenance": provenance,
        }

        if user_id not in ["adminkarl", "admingio", "adminmorgan", "adminesteban"]:
            socketio.emit('new_log', log_data)
    except Exception as e:
        print(f"❌ Une exception s'est produite: {e}")

