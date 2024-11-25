FROM python:3.9-slim

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    libpq-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Script d'attente pour la base de données
COPY scripts/wait-for-db.sh /wait-for-db.sh
RUN chmod +x /wait-for-db.sh

# Copie du projet
COPY . .

EXPOSE 8000

# Commande par défaut
CMD ["/wait-for-db.sh", "python", "manage.py", "runserver", "0.0.0.0:8000"] 