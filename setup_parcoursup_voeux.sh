#!/usr/bin/env bash
set -e

# Vérifier que Python 3 est installé
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 n'est pas installé. Veuillez l'installer avant de continuer."
  exit 1
fi

# Vérifier que pip est installé, sinon l'installer
if ! python3 -m pip --version >/dev/null 2>&1; then
  echo "pip n'est pas trouvé. Installation de pip..."
  python3 -m ensurepip --upgrade || {
    echo "Échec de l'installation de pip. Veuillez installer pip manuellement.";
    exit 1;
  }
fi

# Vérifier que Docker est installé
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker n'est pas installé. Veuillez installer Docker avant de continuer."
  exit 1
fi

# Vérifier que Docker Compose est installé
if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose n'est pas installé. Veuillez installer Docker Compose avant de continuer."
  exit 1
fi

# URLs des fichiers à télécharger
docker_compose_url="https://raw.githubusercontent.com/Karl2301/parcoursup_voeux_jp2/refs/heads/main/docker-compose.yml"
readme_url="https://raw.githubusercontent.com/Karl2301/parcoursup_voeux_jp2/refs/heads/main/README.md"
backup_sql_url="https://raw.githubusercontent.com/Karl2301/parcoursup_voeux_jp2/refs/heads/main/backup_20250504_090243.sql"
commands_url="https://raw.githubusercontent.com/Karl2301/parcoursup_voeux_jp2/refs/heads/main/commandes.txt"

# Première exécution : initialisation
if [ ! -f .env ]; then
  echo "Première exécution : téléchargement des fichiers nécessaires..."
  curl -sSL -o docker-compose.yml "$docker_compose_url"
  curl -sSL -o README.md "$readme_url"
  curl -sSL -o backup_20250504_090243.sql "$backup_sql_url"
  curl -sSL -o commandes.txt "$commands_url"

  cat > .env <<EOF
SMTP_API_KEY=clef-brevo-smtp-api # facultatif mais utile
TURNSTILE_SITE_KEY=clef-TURNSTILE-site
TURNSTILE_SECRET_KEY=clef-TURNSTILE-secret

MYSQL_ROOT_PASSWORD=mot-de-passe-root-mariadb
MYSQL_DATABASE=jp2_voeux_parcoursup
MYSQL_USER=identifiant-mariadb
MYSQL_PASSWORD=mot-de-passe-mariadb

GITHUB_CLIENT_PAT=clef_de_récupération_du_projet

APP_PORT=5000
MARIADB_PORT=3306
EOF

  echo "Fichier .env généré. Veuillez le modifier selon vos besoins, puis relancez ce script."
  exit 0
fi

# Deuxième exécution (ou suivante) : lancement de l'installation
echo "Démarrage de l'installation avec la configuration existante..."
set -o allexport; source .env; set +o allexport && \
  echo "$GITHUB_CLIENT_PAT" | docker login ghcr.io -u karl2301 --password-stdin && \
  docker compose pull && \
  docker compose up -d && \
  docker compose logs -f web db watchtower
