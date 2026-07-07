# ============================================================
# LABO.COS App — Dockerfile
# Multi-stage build : Python 3.11 slim
# ============================================================

# ── Stage 1 : Base ──
FROM python:3.11-slim AS base

# Variables d'environnement Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Dépendances système pour WeasyPrint, psycopg2, Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-liberation \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Stage 2 : Dépendances ──
FROM base AS dependencies

COPY requirements/base.txt requirements/base.txt
COPY requirements/production.txt requirements/production.txt

RUN pip install --upgrade pip && \
    pip install -r requirements/production.txt

# ── Stage 3 : Application ──
FROM dependencies AS app

# Copier le code source
COPY . .

# Créer les dossiers nécessaires
RUN mkdir -p /app/staticfiles /app/media /app/logs

# Collecter les fichiers statiques
RUN DJANGO_SETTINGS_MODULE=labocos.settings.production \
    SECRET_KEY=build-secret-key \
    DATABASE_URL=sqlite:///tmp/build.db \
    python manage.py collectstatic --noinput || true

# Utilisateur non-root pour la sécurité
RUN addgroup --system labocos && \
    adduser --system --ingroup labocos labocos && \
    chown -R labocos:labocos /app

USER labocos

EXPOSE 8000

# Point d'entrée : Gunicorn
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--worker-class", "sync", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "labocos.wsgi:application"]
