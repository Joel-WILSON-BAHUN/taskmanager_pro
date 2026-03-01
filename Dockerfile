FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=taskmanager.settings

WORKDIR /app

# Dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code source
COPY . .

# Collecte des fichiers statiques
RUN python manage.py collectstatic --noinput

# Port
EXPOSE 8000

# Script de démarrage
CMD ["sh", "-c", "python manage.py migrate && python seed_data.py && gunicorn taskmanager.wsgi:application --bind 0.0.0.0:8000 --workers 2"]
