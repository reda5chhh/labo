"""
LABO.COS App — URLs principales (root URL conf).
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    # Administration Django
    path('admin/', admin.site.urls),

    # i18n switcher
    path('i18n/', include('django.conf.urls.i18n')),
]

# URLs avec préfixe langue (ex: /fr/, /ar/)
urlpatterns += i18n_patterns(
    # Authentification
    path('auth/', include('apps.core.urls.auth')),

    # Dashboard principal
    path('', include('apps.core.urls.dashboard')),

    # Applications métier
    path('commercial/', include('apps.commercial.urls')),
    path('finance/', include('apps.finance.urls')),
    path('technique/', include('apps.technique.urls')),
    path('qualite/', include('apps.qualite.urls')),
    path('metrologie/', include('apps.metrologie.urls')),
    path('rh/', include('apps.rh.urls')),
    path('achats/', include('apps.achats.urls')),
    path('ged/', include('apps.ged.urls')),
    path('espace-user/', include('apps.espace_user.urls')),
    path('informatique/', include('apps.informatique.urls')),
    path('parametrage/', include('apps.parametrage.urls')),

    prefix_default_language=False,
)

# Servir les fichiers statiques et médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Debug Toolbar
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
