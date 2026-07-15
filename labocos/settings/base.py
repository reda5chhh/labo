"""
LABO.COS App — Configuration Django (Base)
Paramètres communs à tous les environnements.
"""
from pathlib import Path
import environ

# ============================================================
# Chemins de base
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ============================================================
# Variables d'environnement
# ============================================================
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
    AXES_FAILURE_LIMIT=(int, 5),
    USE_S3=(bool, False),
)
environ.Env.read_env(BASE_DIR / '.env')

# ============================================================
# Sécurité
# ============================================================
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# ============================================================
# Applications installées
# ============================================================
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'crispy_forms',
    'crispy_bootstrap5',
    'axes',
    'storages',
    'django_filters',
    'django_celery_beat',
    'django_celery_results',
]

LOCAL_APPS = [
    'apps.core.apps.CoreConfig',
    'apps.commercial.apps.CommercialConfig',
    'apps.marches.apps.MarchesConfig',
    'apps.facturation_comptabilite.apps.FacturationComptabiliteConfig',
    'apps.achats_logistique.apps.AchatsLogistiqueConfig',
    'apps.gestion_ressources_humaines.apps.GestionRessourcesHumainesConfig',
    'apps.table_receptions.apps.TableReceptionsConfig',
    'apps.gestion_laboratoire.apps.GestionLaboratoireConfig',
    'apps.formation_qualification.apps.FormationQualificationConfig',
    'apps.gestion_documentaire.apps.GestionDocumentaireConfig',
    'apps.fiche_progres.apps.FicheProgresConfig',
    'apps.inventaire_materiel.apps.InventaireMaterielConfig',
    'apps.fiche_vie.apps.FicheVieConfig',
    'apps.etalonnage_interne.apps.EtalonnageInterneConfig',
    'apps.maj_incertitude.apps.MajIncertitudeConfig',
    'apps.maj_elements_etalonner.apps.MajElementsEtalonnerConfig',
    'apps.maj_mouvement_materiel.apps.MajMouvementMaterielConfig',
    'apps.plannings_metrologie.apps.PlanningsMetrologieConfig',
    'apps.capabilite.apps.CapabiliteConfig',
    'apps.exploitation_metrologique.apps.ExploitationMetrologiqueConfig',
    'apps.verification_etuves.apps.VerificationEtuvesConfig',
    'apps.parametres_metrologie.apps.ParametresMetrologieConfig',
    'apps.conges.apps.CongesConfig',
    'apps.attestations.apps.AttestationsConfig',
    'apps.demandes_achat.apps.DemandesAchatConfig',
    'apps.specimen_signature.apps.SpecimenSignatureConfig',
    'apps.archive_ged.apps.ArchiveGedConfig',
    'apps.services_familles_ged.apps.ServicesFamillesGedConfig',
    'apps.droits_ged.apps.DroitsGedConfig',
    'apps.suivi_modifications.apps.SuiviModificationsConfig',
    'apps.gestion_droits_acces.apps.GestionDroitsAccesConfig',
    'apps.donnees_informatique.apps.DonneesInformatiqueConfig',
    'apps.parametrage_general.apps.ParametrageGeneralConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ============================================================
# Middleware
# ============================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
    'apps.core.middleware.AuditLogMiddleware',
    'apps.core.middleware.ServiceSelectionMiddleware',
]

# ============================================================
# URLs & WSGI
# ============================================================
ROOT_URLCONF = 'labocos.urls'
WSGI_APPLICATION = 'labocos.wsgi.application'

# ============================================================
# Templates
# ============================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'apps.core.context_processors.labo_settings',
            ],
        },
    },
]

# ============================================================
# Base de données
# ============================================================
DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:///db.sqlite3'),
}

# connect_timeout uniquement pour PostgreSQL (non supporté par SQLite)
if DATABASES['default']['ENGINE'] != 'django.db.backends.sqlite3':
    DATABASES['default'].setdefault('OPTIONS', {})['connect_timeout'] = 10

# ============================================================
# Modèle utilisateur personnalisé
# ============================================================
AUTH_USER_MODEL = 'core.User'

# ============================================================
# Authentification
# ============================================================
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/auth/login/'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================================
# Internationalisation
# ============================================================
LANGUAGE_CODE = 'fr'
TIME_ZONE = 'Africa/Casablanca'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('fr', 'Français'),
    ('ar', 'العربية'),
    ('en', 'English'),
]

LOCALE_PATHS = [BASE_DIR / 'locale']

# ============================================================
# Fichiers statiques
# ============================================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# ============================================================
# Fichiers médias
# ============================================================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================================
# Stockage S3 (production)
# ============================================================
if env('USE_S3'):
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='eu-west-1')
    AWS_DEFAULT_ACL = 'private'
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# ============================================================
# Email
# ============================================================
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='localhost')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='LABO.COS <noreply@labocos.ma>')

# ============================================================
# Celery
# ============================================================
CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://localhost:6379/1')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# ============================================================
# Django REST Framework
# ============================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
}

# ============================================================
# django-axes (Protection Brute-Force)
# ============================================================
AXES_FAILURE_LIMIT = env('AXES_FAILURE_LIMIT', default=5)
AXES_COOLOFF_TIME = env.int('AXES_COOLOFF_TIME', default=1)  # heure
AXES_LOCKOUT_TEMPLATE = 'registration/lockout.html'
AXES_RESET_ON_SUCCESS = True
AXES_ENABLE_ACCESS_FAILURE_LOG = True

# ============================================================
# Crispy Forms
# ============================================================
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# ============================================================
# Clé primaire par défaut
# ============================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# Taille maximale upload
# ============================================================
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB

# ============================================================
# Paramètres Laboratoire (contexte global)
# ============================================================
LABO_NOM = env('LABO_NOM', default='LABO.COS')
LABO_ADRESSE = env('LABO_ADRESSE', default='Adresse du laboratoire')
LABO_TEL = env('LABO_TEL', default='+212 XX XX XX XX')
LABO_EMAIL = env('LABO_EMAIL', default='contact@labocos.ma')
LABO_SITE = env('LABO_SITE', default='www.labocos.ma')

# ============================================================
# Logging
# ============================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'labocos.log',
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
