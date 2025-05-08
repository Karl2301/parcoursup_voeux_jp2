#!/bin/bash

# Demander le nom d'utilisateur et le mot de passe pour MariaDB
echo "[INFO] CREATION: Veuillez entrer le nom de l'utilisateur MariaDB:"
read -r db_user
echo "[INFO] CREATION: Veuillez entrer le mot de passe pour l'utilisateur MariaDB:"
read -sr db_password  # -s pour masquer la saisie du mot de passe

# Installer MariaDB
echo "[INFO] Installation de MariaDB..."
sudo apt update
sudo apt install -y mariadb-server

# Démarrer MariaDB et l'activer au démarrage
echo "[INFO] Démarrage et activation de MariaDB..."
sudo systemctl start mariadb
sudo systemctl enable mariadb
sudo systemctl status mariadb

# Créer l'utilisateur et les privilèges dans MariaDB
echo "[INFO] Configuration de l'utilisateur MariaDB..."
sudo mariadb -e "CREATE USER '${db_user}'@'localhost' IDENTIFIED BY '${db_password}';"
sudo mariadb -e "GRANT ALL PRIVILEGES ON *.* TO '${db_user}'@'localhost' WITH GRANT OPTION;"
sudo mariadb -e "FLUSH PRIVILEGES;"
sudo mariadb -e "SELECT user, host FROM mysql.user;"
sudo mariadb -e "CREATE DATABASE IF NOT EXISTS jp2_voeux_parcoursup;"

# Importer la base de données depuis un fichier SQL
echo "[INFO] Importation de la base de données..."
sudo mariadb jp2_voeux_parcoursup < backup_20250504_090243.sql
sudo mariadb -e "SHOW TABLES IN jp2_voeux_parcoursup;"

# Installer python3.12-venv
echo "[INFO] Installation de python3.12-venv..."
sudo apt install -y python3.12-venv

# Créer un environnement virtuel
echo "[INFO] Création de l'environnement virtuel..."
python3.12 -m venv .venv

# Installer les dépendances à partir de requirements.txt si le fichier existe
if [ -f "requirements.txt" ]; then
    echo "[INFO] Installation des dépendances Python..."
    ./.venv/bin/pip install -r requirements.txt
else
    echo "[INFO] Aucun fichier requirements.txt trouvé."
fi

# Ajouter un cron pour exécuter le script get_update.sh tous les jours à 4h du matin
echo "[INFO] Ajout de la tâche cron..."
(crontab -l 2>/dev/null; echo "0 4 * * * /bin/bash $(pwd)/get_update.sh >> $(pwd)/cron.log 2>&1") | crontab -

# Terminer
echo "[INFO] Configuration terminée avec succès."
