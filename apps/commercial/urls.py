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
    path('clients/<int:pk>/annuler/', views.ClientAnnulerView.as_view(), name='client_delete'),
    path('clients/<int:pk>/restaurer/', views.ClientRestaurerView.as_view(), name='client_restore'),

    # Revue de Demande
    path('revues-demandes/', views.RevueDemandeListView.as_view(), name='revuedemande_list'),
    path('revues-demandes/creer/', views.RevueDemandeCreateView.as_view(), name='revuedemande_create'),
    path('revues-demandes/<int:pk>/modifier/', views.RevueDemandeUpdateView.as_view(), name='revuedemande_update'),
    path('revues-demandes/<int:pk>/imprimer/', views.RevueDemandePrintView.as_view(), name='revuedemande_print'),
    path('revues-demandes/<int:pk>/annuler/', views.RevueDemandeAnnulerView.as_view(), name='revuedemande_delete'),
    path('revues-demandes/<int:pk>/restaurer/', views.RevueDemandeRestaurerView.as_view(), name='revuedemande_restore'),

    # Devis
    path('devis/', views.DevisListView.as_view(), name='devis_list'),
    path('devis/<int:pk>/', views.DevisDetailView.as_view(), name='devis_detail'),
    path('devis/creer/', views.DevisCreateView.as_view(), name='devis_create'),
    path('devis/<int:pk>/modifier/', views.DevisUpdateView.as_view(), name='devis_update'),
    path('devis/<int:pk>/annuler/', views.DevisAnnulerView.as_view(), name='devis_delete'),
    path('devis/<int:pk>/restaurer/', views.DevisRestaurerView.as_view(), name='devis_restore'),
    path('devis/affecter/', views.AffecterDossierDevisView.as_view(), name='devis_affecter'),
    path('devis/action/', views.DevisActionView.as_view(), name='devis_action'),

    # Dossiers
    path('dossiers/', views.DossierListView.as_view(), name='dossier_list'),
    path('dossiers/<int:pk>/', views.DossierDetailView.as_view(), name='dossier_detail'),
    path('dossiers/creer/', views.DossierCreateView.as_view(), name='dossier_create'),
    path('dossiers/<int:pk>/modifier/', views.DossierUpdateView.as_view(), name='dossier_update'),
    path('dossiers/<int:pk>/annuler/', views.DossierAnnulerView.as_view(), name='dossier_delete'),
    path('dossiers/<int:pk>/restaurer/', views.DossierRestaurerView.as_view(), name='dossier_restore'),

    # Conventions
    path('conventions/', views.ConventionListView.as_view(), name='convention_list'),
    path('conventions/<int:pk>/', views.ConventionDetailView.as_view(), name='convention_detail'),
    path('conventions/creer/', views.ConventionCreateView.as_view(), name='convention_create'),
    path('conventions/<int:pk>/modifier/', views.ConventionUpdateView.as_view(), name='convention_update'),
    path('conventions/<int:pk>/annuler/', views.ConventionAnnulerView.as_view(), name='convention_delete'),
    path('conventions/<int:pk>/restaurer/', views.ConventionRestaurerView.as_view(), name='convention_restore'),
    path('conventions/valider/', views.ConventionValiderView.as_view(), name='convention_valider'),

    # Bons de livraison
    path('bons-livraison/', views.BLListView.as_view(), name='bl_list'),
    path('bons-livraison/<int:pk>/', views.BLDetailView.as_view(), name='bl_detail'),
    path('bons-livraison/creer/', views.BLCreateView.as_view(), name='bl_create'),
    path('bons-livraison/<int:pk>/modifier/', views.BLUpdateView.as_view(), name='bl_update'),
    path('bons-livraison/<int:pk>/annuler/', views.BLAnnulerView.as_view(), name='bl_delete'),
    path('bons-livraison/<int:pk>/restaurer/', views.BLRestaurerView.as_view(), name='bl_restore'),

    # AJAX HTMX Dropdowns
    path('ajax/load-devis/', views.ajax_load_devis, name='ajax_load_devis'),
    path('ajax/load-dossiers/', views.ajax_load_dossiers, name='ajax_load_dossiers'),
    path('ajax/load-revues/', views.ajax_load_revues, name='ajax_load_revues'),
    path('ajax/load-bl-details/', views.BLDetailAjaxView.as_view(), name='ajax_load_bl_details'),

    # Actions Bon de Livraison
    path('bons-livraison/<int:pk>/marquer-envoye/', views.bl_mark_sent, name='bl_mark_sent'),
    path('bons-livraison/<int:pk>/basculer-accuse/', views.bl_toggle_accuse, name='bl_toggle_accuse'),
]

