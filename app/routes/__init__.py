"""
Ce fichier sert de point d'entrée pour l'importation et la gestion des routes de l'application web. 
Il regroupe et organise les différents modules de gestion des routes, permettant ainsi de centraliser 
les fonctionnalités et de simplifier leur utilisation dans l'application.

### Fonctionnalités principales :
- Gestion des authentifications (login, logout, récupération d'identifiants, changement de mot de passe).
- Gestion des pages principales (accueil, tableau de bord, paramètres, aide, etc.).
- Gestion des données (récupération, mise à jour, téléchargement, et importation de fichiers CSV).
- Gestion des notifications et des interactions en temps réel via WebSocket.
- Administration (tableau de bord admin, suppression de données, gestion des professeurs, etc.).
- Gestion des préférences utilisateur (thème, nom d'utilisateur, tutoriels, etc.).
- Gestion des statuts et des validations (voeux, deadlines, etc.).

Ce fichier permet de centraliser toutes les routes nécessaires au bon fonctionnement de l'application, 
en facilitant leur importation et leur utilisation dans d'autres parties du projet.
"""

from .login_get import login_get
from .login_post import login_post
from .home import home
from .dashboard import dashboard
from .logout import logout
from .get_data import get_data
from .update_data import update_data
from .settings import settings
from .lost_id import lost_id_get, lost_id_post
from .update_theme import update_theme, get_theme
from .change_password import change_password_post, change_password_get
from .aide import aide_get, aide_post
from .configure_password import configure_password_get, configure_password_post
from .configure_prof import configure_prof_get, configure_prof_post
from .websocket import *
from .classes_prof import classes_prof_get
from .profil_eleve import profil_eleve_get
from .notifications import get_notifications, format_datetime
from .upload_csv import process_csv, upload_csv, upload_csv_get
from .download_voeux import download_voeux, download_voeux_users_classe
from .admin_dashboard import admin_dashboard
from .delete_notifs import delete_demande
from .delete_prof import delete_prof
from .status import status
from .deadline import deadline_post
from .notif_voeux_invalide import notif_voeux_invalide
from .reset_password import reset_student_password
from .licence import licence
from .reset_voeux_validation import reset_voeux_validation_post
from .save_prof_data import save_prof_data
from .get_prof_data import get_prof_data
from .voeux_status import get_voeux_status, post_voeux_status
from .didacticiel import didacticiel_post, didacticiel_get
from .change_username import change_username_get, change_username_post
from .robot import robot
from .statistiques import statistiques_get, statistiques_get_data
from .log import log_get
from .siteweb import siteweb_get
from .update_config import update_config_post
from .admin_reset_password import admin_reset_password_post
from .active_email import post_want_email_on_all_validation
from .log_fingerprint import log_fingerprint
from .forceValidation import force_validation
from .maintenance import maintenance_get