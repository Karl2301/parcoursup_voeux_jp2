#!/bin/bash

# === Répertoire du script ===
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR" || exit 1

# === Vérification de python et installation de python-is-python3 si manquant ===
if ! command -v python >/dev/null 2>&1; then
    echo "[INFO] $(date): 'python' non trouvé. Installation de python-is-python3..."
    sudo apt update
    sudo apt install -y python-is-python3
fi

# === Vérification/installation python3-venv, pip et virtualenv ===
if ! python3 -m venv --help >/dev/null 2>&1; then
    echo "[WARN] $(date): python3-venv absent. Installation..."
    sudo apt update
    sudo apt install -y python3 python3-venv python3-pip python3-virtualenv
fi

# === GIT : Cloner ou mettre à jour ===
if [ -d .git ]; then
    echo "[INFO] $(date): Dépôt Git détecté."
    git reset --hard origin/main
    git checkout main
    git fetch origin

    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse @{u})

    if [ "$LOCAL" != "$REMOTE" ]; then
        echo "[INFO] $(date): Mise à jour disponible. Pull..."
        git pull origin main
        # Si la mise à jour a eu lieu, on garde une trace pour redémarrer le service
        UPDATED=true
    else
        echo "[INFO] $(date): Dépôt déjà à jour."
        UPDATED=false
    fi
else
    echo "[INFO] $(date): Aucun dépôt Git trouvé. Clonage..."
    rm -rf ./* ./.??*
    git clone https://github.com/Karl2301/parcoursup_voeux_jp2.git .
fi

# === Création .venv si manquant ou corrompu ===
if [ ! -d ".venv" ] || [ ! -x ".venv/bin/python3" ]; then
    echo "[INFO] $(date): (Re)création de l'environnement virtuel..."
    rm -rf .venv
    python3 -m venv .venv

    # Forcer installation de pip si nécessaire
    if [ ! -x ".venv/bin/pip" ]; then
        echo "[WARN] $(date): pip manquant dans .venv, tentative de récupération..."
        source .venv/bin/activate
        python -m ensurepip --upgrade
        deactivate
    fi
fi

# === Installation des dépendances Python ===
if [ -f "requirements.txt" ]; then
    echo "[INFO] $(date): Installation des dépendances Python..."
    ./.venv/bin/pip install --upgrade pip
    ./.venv/bin/pip install -r requirements.txt
else
    echo "[WARN] $(date): requirements.txt manquant."
fi

# === Vérification si le service existe ===
SERVICE_NAME="voeuxjpdeux.service"
if ! systemctl is-active --quiet $SERVICE_NAME; then
    echo "[INFO] $(date): Le service $SERVICE_NAME n'existe pas. Création et démarrage..."

    # Création du fichier de service systemd avec chemin dynamique
    sudo bash -c "cat > /etc/systemd/system/$SERVICE_NAME <<EOF
[Unit]
Description=Voeux JP2 Service
After=network.target

[Service]
ExecStart=$PROJECT_DIR/.venv/bin/python $PROJECT_DIR/app/app.py
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/.venv/bin:/usr/bin:/bin
Environment=VIRTUAL_ENV=$PROJECT_DIR/.venv
Restart=always
User=voeux
Group=voeux

[Install]
WantedBy=multi-user.target
EOF"

    # Recharger systemd pour prendre en compte le nouveau service
    sudo systemctl daemon-reload

    # Démarrer et activer le service pour qu'il démarre au démarrage
    sudo systemctl start $SERVICE_NAME
    sudo systemctl enable $SERVICE_NAME
    echo "[INFO] $(date): Service $SERVICE_NAME créé et démarré."
else
    echo "[INFO] $(date): Le service $SERVICE_NAME est déjà actif."
fi

# === Si une mise à jour a eu lieu, redémarrer le service ===
if [ "$UPDATED" = true ]; then
    echo "[INFO] $(date): Nouveau commit détecté. Redémarrage du service..."
    sudo systemctl restart $SERVICE_NAME
    echo "[INFO] $(date): Service $SERVICE_NAME redémarré."
else
    echo "[INFO] $(date): Aucune mise à jour détectée, le service n'a pas été redémarré."
fi
