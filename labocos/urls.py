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
    path('marches/', include('apps.marches.urls')),
    path('facturation-comptabilite/', include('apps.facturation_comptabilite.urls')),
    path('achats-logistique/', include('apps.achats_logistique.urls')),
    path('gestion-ressources-humaines/', include('apps.gestion_ressources_humaines.urls')),
    path('table-receptions/', include('apps.table_receptions.urls')),
    path('gestion-laboratoire/', include('apps.gestion_laboratoire.urls')),
    path('formation-qualification/', include('apps.formation_qualification.urls')),
    path('gestion-documentaire/', include('apps.gestion_documentaire.urls')),
    path('fiche-progres/', include('apps.fiche_progres.urls')),
    path('inventaire-materiel/', include('apps.inventaire_materiel.urls')),
    path('fiche-vie/', include('apps.fiche_vie.urls')),
    path('etalonnage-interne/', include('apps.etalonnage_interne.urls')),
    path('maj-incertitude/', include('apps.maj_incertitude.urls')),
    path('maj-elements-etalonner/', include('apps.maj_elements_etalonner.urls')),
    path('maj-mouvement-materiel/', include('apps.maj_mouvement_materiel.urls')),
    path('plannings-metrologie/', include('apps.plannings_metrologie.urls')),
    path('capabilite/', include('apps.capabilite.urls')),
    path('exploitation-metrologique/', include('apps.exploitation_metrologique.urls')),
    path('verification-etuves/', include('apps.verification_etuves.urls')),
    path('parametres-metrologie/', include('apps.parametres_metrologie.urls')),
    path('conges/', include('apps.conges.urls')),
    path('attestations/', include('apps.attestations.urls')),
    path('demandes-achat/', include('apps.demandes_achat.urls')),
    path('specimen-signature/', include('apps.specimen_signature.urls')),
    path('archive-ged/', include('apps.archive_ged.urls')),
    path('services-familles-ged/', include('apps.services_familles_ged.urls')),
    path('droits-ged/', include('apps.droits_ged.urls')),
    path('suivi-modifications/', include('apps.suivi_modifications.urls')),
    path('gestion-droits-acces/', include('apps.gestion_droits_acces.urls')),
    path('donnees-informatique/', include('apps.donnees_informatique.urls')),
    path('parametrage-general/', include('apps.parametrage_general.urls')),

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
