# Parcoursup Voeux JP2
sudo cat /home/quasardev/parcoursup_voeux_jp2/20250426_020001.sql | sudo docker exec -i db mariadb -u nsidb -p'123nsi!bd' jp2_voeux_parcoursup
## Description

Parcoursup Voeux JP2 est une application de gestion des élèves et des professeurs dans un lycée, facilitant la modification des choix Parcoursup des élèves tout en permettant aux professeurs de gérer les informations des élèves. L'application offre une interface utilisateur intuitive pour les élèves, les professeurs et les administrateurs.

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
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
- Node.js et npm
- MySQL

### Étapes d'installation

1. Clonez le dépôt :
    ```sh
    git clone https://github.com/votre-utilisateur/parcoursup_voeux_jp2.git
    cd parcoursup_voeux_jp2
    ```

2. Installez les dépendances Python :
    ```sh
    pip install -r requirements.txt
    ```

3. Installez les dépendances JavaScript :
    ```sh
    npm install
    ```

4. Configurez la base de données MySQL :
    ```sh
    mysql -u root -p
    CREATE DATABASE jp2_voeux_parcoursup;
    ```

5. Configurez les variables d'environnement :
    ```sh
    cp .env.example .env
    ```

6. Initialisez la base de données :
    ```sh
    python create_classes.py
    ```

## Configuration

Modifiez le fichier `.env` pour configurer les paramètres de votre base de données et d'autres variables d'environnement nécessaires.

## Utilisation

### Démarrer l'application

1. Lancez le serveur Flask :
    ```
    gunicorn --bind 0.0.0.0:5000 --forwarded-allow-ips="*" --worker-class eventlet -w 1 app:app
    ```

2. Accédez à l'application via `http://ip_machine:5000`.

### Tests

Pour exécuter les tests, utilisez la commande suivante :
    ```sh
    pytest
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