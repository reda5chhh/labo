"""
LABO.COS App — URLs de l'application commercial.
"""
from django.urls import path
from . import views

app_name = 'commercial'

urlpatterns = [
    # Clients
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/creer/', views.ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/modifier/', views.ClientUpdateView.as_view(), name='client_update'),
    path('clients/<int:pk>/supprimer/', views.ClientDeleteView.as_view(), name='client_delete'),

    # Revue de Demande
    path('revues-demandes/', views.RevueDemandeListView.as_view(), name='revuedemande_list'),
    path('revues-demandes/creer/', views.RevueDemandeCreateView.as_view(), name='revuedemande_create'),
    path('revues-demandes/<int:pk>/modifier/', views.RevueDemandeUpdateView.as_view(), name='revuedemande_update'),
    path('revues-demandes/<int:pk>/imprimer/', views.RevueDemandePrintView.as_view(), name='revuedemande_print'),

    # Devis
    path('devis/', views.DevisListView.as_view(), name='devis_list'),
    path('devis/<int:pk>/', views.DevisDetailView.as_view(), name='devis_detail'),
    path('devis/creer/', views.DevisCreateView.as_view(), name='devis_create'),
    path('devis/<int:pk>/modifier/', views.DevisUpdateView.as_view(), name='devis_update'),
    path('devis/<int:pk>/supprimer/', views.DevisDeleteView.as_view(), name='devis_delete'),
    path('devis/affecter/', views.AffecterDossierDevisView.as_view(), name='devis_affecter'),
    path('devis/action/', views.DevisActionView.as_view(), name='devis_action'),

    # Dossiers
    path('dossiers/', views.DossierListView.as_view(), name='dossier_list'),
    path('dossiers/<int:pk>/', views.DossierDetailView.as_view(), name='dossier_detail'),
    path('dossiers/creer/', views.DossierCreateView.as_view(), name='dossier_create'),
    path('dossiers/<int:pk>/modifier/', views.DossierUpdateView.as_view(), name='dossier_update'),
    path('dossiers/<int:pk>/supprimer/', views.DossierDeleteView.as_view(), name='dossier_delete'),

    # Conventions
    path('conventions/', views.ConventionListView.as_view(), name='convention_list'),
    path('conventions/<int:pk>/', views.ConventionDetailView.as_view(), name='convention_detail'),
    path('conventions/creer/', views.ConventionCreateView.as_view(), name='convention_create'),
    path('conventions/<int:pk>/modifier/', views.ConventionUpdateView.as_view(), name='convention_update'),
    path('conventions/<int:pk>/supprimer/', views.ConventionDeleteView.as_view(), name='convention_delete'),

    # Appels d'offres, Cautions, Décomptes (Vue regroupée en onglets)
    path('appels-offres/', views.AOListView.as_view(), name='ao_list'),

    # AOSoumission
    path('appels-offres/soumissions/creer/', views.AOSoumissionCreateView.as_view(), name='aosoumission_create'),
    path('appels-offres/soumissions/<int:pk>/modifier/', views.AOSoumissionUpdateView.as_view(), name='aosoumission_update'),

    # AOAdjuge
    path('appels-offres/adjudications/creer/', views.AOAdjugeCreateView.as_view(), name='aoadjuge_create'),
    path('appels-offres/adjudications/<int:pk>/modifier/', views.AOAdjugeUpdateView.as_view(), name='aoadjuge_update'),

    # Cautions
    path('cautions/creer/', views.CautionCreateView.as_view(), name='caution_create'),
    path('cautions/<int:pk>/modifier/', views.CautionUpdateView.as_view(), name='caution_update'),

    # Décomptes
    path('decomptes/creer/', views.DecompteCreateView.as_view(), name='decompte_create'),
    path('decomptes/<int:pk>/modifier/', views.DecompteUpdateView.as_view(), name='decompte_update'),

    # Bons de livraison
    path('bons-livraison/', views.BLListView.as_view(), name='bl_list'),
    path('bons-livraison/<int:pk>/', views.BLDetailView.as_view(), name='bl_detail'),
    path('bons-livraison/creer/', views.BLCreateView.as_view(), name='bl_create'),
    path('bons-livraison/<int:pk>/modifier/', views.BLUpdateView.as_view(), name='bl_update'),
    path('bons-livraison/<int:pk>/supprimer/', views.BLDeleteView.as_view(), name='bl_delete'),

    # Résultats / Enquêtes satisfaction
    path('resultats-bc/', views.ResultatBCListView.as_view(), name='resultatbc_list'),
    path('resultats-bc/creer/', views.ResultatBCCreateView.as_view(), name='resultatbc_create'),

    # AJAX HTMX Dropdowns
    path('ajax/load-devis/', views.ajax_load_devis, name='ajax_load_devis'),
    path('ajax/load-dossiers/', views.ajax_load_dossiers, name='ajax_load_dossiers'),
    path('ajax/load-revues/', views.ajax_load_revues, name='ajax_load_revues'),

    # Actions Bon de Livraison
    path('bons-livraison/<int:pk>/marquer-envoye/', views.bl_mark_sent, name='bl_mark_sent'),
    path('bons-livraison/<int:pk>/basculer-accuse/', views.bl_toggle_accuse, name='bl_toggle_accuse'),
]
