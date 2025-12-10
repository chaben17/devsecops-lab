# 1. Image de base (celle que tu as choisie)
FROM python:3.13

# 2. On définit le dossier de travail à l'intérieur du conteneur
WORKDIR /app

# 3. On copie d'abord les requirements (pour profiter du cache Docker)
COPY requirements.txt .

# 4. On installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# 5. On copie le reste du code (main.py)
COPY main.py .

# 6. La commande de démarrage
# Note importante : "--host 0.0.0.0" est obligatoire dans Docker pour être accessible de l'extérieur
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
