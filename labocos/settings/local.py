"""
LABO.COS App — Configuration Django (Développement Local)
Hérite de base.py et active les outils de debug.
"""
from .base import *  # noqa: F401, F403

# ============================================================
# Debug activé
# ============================================================
DEBUG = True

# ============================================================
# Base de données SQLite en fallback si DATABASE_URL absent
# ============================================================
# La valeur est déjà gérée dans base.py via env.db()

# ============================================================
# Django Debug Toolbar (désactivé lors des tests)
# ============================================================
import sys
TESTING = 'test' in sys.argv or any('pytest' in arg for arg in sys.argv)

# Import debug_toolbar conditionally
try:
    import debug_toolbar  # noqa: F401
    has_debug_toolbar = True
except ImportError:
    has_debug_toolbar = False

if not TESTING and has_debug_toolbar:
    INSTALLED_APPS += ['debug_toolbar']  # noqa: F405
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']  # noqa: F405
    INTERNAL_IPS = ['127.0.0.1', '::1', '172.16.0.0/12', '10.0.0.0/8', '192.168.0.0/16'] # Add docker subnets to internal IPs
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
    }

# ============================================================
# Emails : affichage dans la console en dev
# ============================================================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ============================================================
# Sécurité assouplie en dev
# ============================================================
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# ============================================================
# Configuration spéciale pour les tests
# ============================================================
if TESTING:
    AXES_ENABLED = False
    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
    ]
