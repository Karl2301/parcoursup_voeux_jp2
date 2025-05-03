# Utilise une image officielle Python légère
FROM python:3.12-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier requirements.txt dans l'image
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le reste du code
COPY app/ /app

# Exposer le port si nécessaire

# Commande pour lancer ton app
CMD ["python", "app.py"]

