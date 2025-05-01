# Parcoursup Voeux JP2

## Description

Parcoursup Voeux JP2 est une application de gestion des élèves et des professeurs dans un lycée, permettant de classer les voeux ParcourSup des élèves tout en permettant aux professeurs de gérer les informations des élèves. L'application offre une interface utilisateur intuitive pour les élèves, les professeurs et les administrateurs.u

### Cette application ne communique pas avec le site ParcourSup

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Mettre à jour les applications manuellement](#Mettre-à-jour-les-applications-manuellement)
- [Logs](#logs)
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

    ```
    sudo apt-get update
    sudo apt-get install docker-compose-plugin
    ```

3. Vérifier l'installation de docker-compose :

    ```
    docker compose version
    ```

4. Cloner le docker-compose :

    ```
    curl -O https://raw.githubusercontent.com/Karl2301/parcoursup_voeux_jp2/refs/heads/main/docker-compose.yml
    ```

5. Configurez les variables d'environnement dans le meme dossier que le docker-compose.yml :

    ```
    nano .env
    ```
    ou
    ```
    vi .env
    ```

6. Collez et remplissez les informations suivantes dans le fichier `.env`:

    ```
    SMTP_API_KEY=clef-brevo-smtp-api (facultatif)
    TURNSTILE_SITE_KEY=clef-TURNSTILE-site
    TURNSTILE_SECRET_KEY=clef-TURNSTILE-secret

    MYSQL_ROOT_PASSWORD=mot-de-passe-root-mariadb
    MYSQL_DATABASE=jp2_voeux_parcoursup
    MYSQL_USER=identifiant-mariadb
    MYSQL_PASSWORD=mot-de-passe-mariadb

    APP_PORT=5000
    MARIADB_PORT=3306
    ```

6. Initialisez l'application :

    ```
    docker compose up --build -d
    ```

## Configuration

Modifiez le fichier `.env` pour configurer les paramètres de votre base de données et d'autres variables d'environnement nécessaires.

## Utilisation

### Démarrer l'application

1. Lancez l'application (se placer dans le dossier docker-compose.yml) :

    ```
    docker compose up --build -d
    ```

2. Stopper l'application (se placer dans le dossier docker-compose.yml) :

    ```
    docker compose stop
    ```

3. Supprimer l'application (se placer dans le dossier docker-compose.yml) :

    ```
    docker compose down
    ```

4. Accédez à l'application via `http://ip_machine:5000`.

## Mettre à jour les applications manuellement

1. Pour mettre à jour l'application:
Se placer dans le dossier de l'application (où se trouve le fichier docker-compose.yml)

    ```
    docker compose pull
    ```

2. Puis ensuite:

    ```
    docker compose up --build -d
    ```

## Logs

1. Pour voir les logs des conteneur:

    ```
    docker ps
    ```

2. Puis ensuite tapez :

    ```
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
