"""
Fichier: status.py

Ce fichier contient les routes liées à la gestion du statut de l'application.
Il fournit une fonctionnalité simple pour vérifier si l'application est en cours d'exécution
et répondre avec un statut "OK" accompagné du code HTTP 200.

Fonctionnalités :
- Vérification de l'état de santé de l'application via une route dédiée.

Ce fichier est utilisé pour des vérifications basiques de disponibilité et peut être
intégré dans des systèmes de monitoring ou des tests automatisés.
"""

from ext_config import *

def status():
    return 'OK', 200