import schedule
import threading
import time
from datetime import datetime

# Variable globale pour conserver le thread en cours d'exécution
current_thread = None

# Fonction à exécuter programmatiquement
def ma_fonction():
    print(f"Exécution de la fonction à {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Fonction pour planifier l'exécution à une date/heure précise
def planifier_execution(date_heure): #appel de la fonction dans deadline.py (l.40)
    global current_thread

    # Annuler la précédente planification, si un thread existe et est actif
    if current_thread and current_thread.is_alive():
        schedule.clear()
        print("Ancienne tâche annulée.")

    # Convertir la chaîne de caractères en objet datetime
    dt_obj = date_heure

    # Planifier la tâche : la fonction sera exécutée chaque jour à l'heure spécifiée
    schedule.every().day.at(dt_obj.strftime("%H:%M:%S")).do(ma_fonction)

    # Fonction qui exécute en continu les tâches planifiées
    def run_schedule():
        while True:
            schedule.run_pending()
            time.sleep(1)

    # Démarrer le scheduler dans un thread en arrière-plan
    current_thread = threading.Thread(target=run_schedule, daemon=True)
    current_thread.start()
    print(f"Tâche planifiée pour {date_heure}")