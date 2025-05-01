# Parcoursup Voeux JP2

## Description

Parcoursup Voeux JP2 est une application de gestion des élèves et des professeurs dans un lycée, permettant de classer les voeux ParcourSup des élèves tout en permettant aux professeurs de gérer les informations des élèves. L'application offre une interface utilisateur intuitive pour les élèves, les professeurs et les administrateurs.u

### Cette application ne communique pas avec le site ParcourSup

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Mettre à jour les applications manuellement](#maj)
- [Logs] (#logs)
- [Structure du projet](#structure-du-projet)
- [API](#api)
- [Contributions](#contributions)
- [Licence](#licence)

## Fonctionnalités

- **Gestion des élèves et des professeurs**
  - Création, modification et suppression des comptes élèves et professeurs.
  - Liaison des élèves à leurs classes respectives.
  - Gestion des vœux Parcoursup des élèves.

- **Dashboard interactif**
  - Affichage des statistiques en temps réel.
  - Notifications et messages pour les élèves et les professeurs.
  - Validation et téléchargement des vœux des élèves.

- **Sécurité et authentification**
  - Authentification des utilisateurs avec gestion des sessions.
  - Réinitialisation des mots de passe.
  - Gestion des identifiants perdus.

- **Administration**
  - Gestion des comptes administrateurs et super administrateurs.
  - Configuration des paramètres de l'application.
  - Planification des tâches et gestion des deadlines.

## Installation

### Prérequis

- Python 3.8 ou supérieur

### Étapes d'installation

1. Installer Docker Engine :
    ```sh
    # Add Docker's official GPG key:
    sudo apt-get update
    sudo apt-get install ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    ```

2. Installer Docker-Compose :
    ```sh
    sudo apt-get update
    sudo apt-get install docker-compose-plugin
    ```

3. Vérifier l'installation de docker-compose :
    ```sh
    docker compose version
    ```

4. Cloner le docker-compose :
    ```sh
    curl -O https://raw.githubusercontent.com/Karl2301/parcoursup_voeux_jp2/refs/heads/main/docker-compose.yml
    ```

5. Configurez les variables d'environnement dans le meme dossier que le docker-compose.yml :
    ```sh
    nano .env
    ```
    ou
    ```sh
    vi .env
    ```

    Collez et remplissez les informations suivantes dans le fichier `.env`:
    ```
    DATABASE_URL=mysql+pymysql://nsidb:123nsi!bd@db:3306/jp2_voeux_parcoursup
    SMTP_API_KEY=clef-brevo-smtp-api (facultatif)
    TURNSTILE_SITE_KEY=clef-TURNSTILE-site
    TURNSTILE_SECRET_KEY=clef-TURNSTILE-secret

    MYSQL_ROOT_PASSWORD=mot-de-passe-root-mariadb
    MYSQL_DATABASE=jp2_voeux_parcoursup
    MYSQL_USER=identifiant-mariadb
    MYSQL_PASSWORD=mot-de-passe-mariadb
    ```

6. Initialisez l'application :
    ```sh
    docker compose up --build -d
    ```

## Configuration

Modifiez le fichier `.env` pour configurer les paramètres de votre base de données et d'autres variables d'environnement nécessaires.

## Utilisation

### Démarrer l'application

1. Lancez l'application (se placer dans le dossier docker-compose.yml) :
    ```sh
    docker compose up --build -d
    ```
2. Stopper l'application (se placer dans le dossier docker-compose.yml) :
    ```sh
    docker compose stop
    ```

3. Supprimer l'application (se placer dans le dossier docker-compose.yml) :
    ```sh
    docker compose down
    ```

4. Accédez à l'application via `http://ip_machine:5000`.

### Mettre à jour les applications manuellement

Pour mettre à jour l'application:
    Se placer dans le dossier de l'application (où se trouve le fichier docker-compose.yml)
    ```sh
    docker compose pull
    ```
    puis:

    ```sh
    docker compose up --build -d
    ```

### Logs

Pour voir les logs des conteneur:
    ```sh
    docker ps
    ```
    puis:

    ```sh
    docker compose logs -f {nom ou id du conteneur}
    ```

## Structure du projet
    ```
    parcoursup_voeux_jp2/
    ├── .gitignore
    ├── [`admin.py`](admin.py )
    ├── [`app.py`](app.py )
    ├── [`create_classes.py`](create_classes.py )
    ├── [`ext_config.py`](ext_config.py )
    ├── [`fonctions.py`](fonctions.py )
    ├── LICENCE
    ├── [`README.md`](README.md )
    ├── [`SQLClassSQL.py`](SQLClassSQL.py )
    ├── [`todo.md`](todo.md )
    ├── __pycache__/
    ├── .vscode/
    ├── routes/
    │   ├── [`routes/__init__.py`](routes/__init__.py )
    │   ├── admin_dashboard.py
    │   ├── [`routes/aide.py`](routes/aide.py )
    │   └── ...
    ├── static/
    │   ├── css/
    │   ├── js/
    │   └── ...
    ├── templates/
    │   ├── dashboard_super_administrateur/
    │   ├── classes/
    │   ├── configure_password/
    │   ├── dashboard_prof/
    │   ├── login/
    │   ├── notifications/
    │   └── ...
    ```

## API

    ### Endpoints principaux
        - `GET /login` : Affiche la page de connexion.
        - `POST /login` : Authentifie l'utilisateur.
        - `GET /dashboard` : Affiche le tableau de bord de l'utilisateur.
        - `POST /configure_password` : Configure le mot de passe de l'utilisateur.
        - `POST /upload_csv` : Permet de télécharger un fichier CSV.
        - `POST /save_prof_data` : Sauvegarde les données d'un professeur.
        - `POST /validate_voeux` : Valide les vœux d'un élève.


### Contributions
        - Les contributions sont les bienvenues ! Veuillez contacter les propriétaires via mail situé sur la page de licence.

## Licence
    Ce projet est sous licence. Voir le fichier LICENCE pour plus de détails.
