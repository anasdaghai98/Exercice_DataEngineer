# Utilisez l'image Python officielle en tant qu'image parente
FROM python:3.9-slim

# Définition du répertoire de travail dans le conteneur
WORKDIR /app

# Copiez les fichiers requis pour l'application FastAPI
COPY requirements.txt .
COPY main.py .

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port 8000 sur le conteneur
EXPOSE 8000

# Commande pour exécuter l'application FastAPI via uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
