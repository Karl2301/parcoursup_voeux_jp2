# Parcoursup Voeux JP2

## Description

Parcoursup Voeux JP2 est une application de gestion des élèves et des professeurs dans un lycée, permettant de classer les voeux ParcourSup des élèves tout en permettant aux professeurs de gérer les informations des élèves. L'application offre une interface utilisateur intuitive pour les élèves, les professeurs et les administrateurs.

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
- Git

### Étapes d'installation

1. Installer Docker Engine :
	```
	# Créer un dossier de projet:
	mkdir voeuxjp2
	cd voeuxjp2
	
	# Cloner le repo github dans le dossier de projet:
	git clone https://github.com/Karl2301/parcoursup_voeux_jp2.git temp_clone
	cp -r temp_clone/* temp_clone/.* .
	rm -rf temp_clone
	```

2. Configurez les variables d'environnement dans le meme dossier:

	```
	nano .env
	```
	ou
	```
	vi .env
	```

3. Collez et remplissez les informations suivantes dans le fichier `.env`:

	```
	SMTP_API_KEY={clé brevo smtp pour la notification par email}
	
	MYSQL_ROOT_PASSWORD={mot de passe root mariadb}
	MYSQL_DATABASE={nom de la base mariadb}
	MYSQL_USER={nom d'utilisateur mariadb}
	MYSQL_PASSWORD={mot de passe mariadb}
	
	GITHUB_CLIENT_PAT=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
	
	MARIADB_PORT=3306
	APP_PORT=5000
	```

4. Donner les droits d'execution aux scripts:
	```
	chmod 777 setup_parcoursup_voeux.sh get_update.sh
	```
6. Executer le script d'installation une seul fois:
   Rentrez les informations de connexion de votre database après avoir exécuté ce script:
	```
	sudo ./setup_parcoursup_voeux.sh
	```

## Configuration

Modifiez le fichier `.env` pour configurer les paramètres de votre base de données et d'autres variables d'environnement nécessaires.

## Utilisation

### Démarrer l'application

1. Lancez l'application :

	```
	sudo systemctl start voeuxjpdeux.service
	```

2. Stopper l'application :

	```
	sudo systemctl stop voeuxjpdeux.service
	```



4. Accédez à l'application via `http://ip_machine:{APP_PORT}`.

## Mettre à jour les applications manuellement

Pour mettre à jour l'application, se placer dans le dossier de l'application:

	```
	sudo ./get_update.sh
	```

## Logs

Pour voir les logs de l'application web:

	```
	sudo journalctl -u voeuxjpdeux.service -f
	```

Pour voir les logs de MariaDB :

	```
	sudo journalctl -u mariadb.service -f
	```


## Structure du projet

```
parcoursup_voeux_jp2/
├── .gitignore
├── [admin.py](admin.py )
├── [app.py](app.py )
├── [create_classes.py](create_classes.py )
├── [ext_config.py](ext_config.py )
├── [fonctions.py](fonctions.py )
├── LICENCE
├── [README.md](README.md )
├── [SQLClassSQL.py](SQLClassSQL.py )
├── [todo.md](todo.md )
├── __pycache__/
├── .vscode/
├── routes/
│   ├── [routes/__init__.py](routes/__init__.py )
│   ├── admin_dashboard.py
│   ├── [routes/aide.py](routes/aide.py )
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
- Les contributions sont les bienvenues ! Veuillez contacter les propriétaires en créant une issue sur ce github.

## Licence
Ce projet est sous licence. Voir le fichier LICENCE pour plus de détails.
