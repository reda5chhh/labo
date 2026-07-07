"""Routage des URLs pour le module Finance."""
from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    # Fournisseurs
    path('fournisseurs/', views.FournisseurListView.as_view(), name='fournisseur_list'),
    path('fournisseurs/ajouter/', views.FournisseurCreateView.as_view(), name='fournisseur_create'),
    path('fournisseurs/<int:pk>/modifier/', views.FournisseurUpdateView.as_view(), name='fournisseur_update'),

    # Factures Clients (Facturation)
    path('factures/', views.FactureListView.as_view(), name='facture_list'),
    path('factures/ajouter/', views.FactureCreateView.as_view(), name='facture_create'),
    path('factures/<int:pk>/', views.FactureDetailView.as_view(), name='facture_detail'),
    path('factures/<int:pk>/modifier/', views.FactureUpdateView.as_view(), name='facture_update'),
    path('factures/<int:pk>/signer/', views.FactureSignView.as_view(), name='facture_sign'),
    path('factures/<int:pk>/recouvrement/', views.FactureUpdateRecouvrementView.as_view(), name='facture_update_recouvrement'),

    # Facturation Réception
    path('factures-receptions/', views.FactureReceptionListView.as_view(), name='facture_reception_list'),
    path('factures-receptions/facturer/', views.FactureGroupedCreateView.as_view(), name='facture_grouped_create'),

    # Encaissements Clients
    path('encaissements/', views.EncaissementListView.as_view(), name='encaissement_list'),
    path('encaissements/ajouter/', views.EncaissementCreateView.as_view(), name='encaissement_create'),

    # Caisse
    path('caisse/', views.CaisseListView.as_view(), name='caisse_list'),
    path('caisse/mouvement/ajouter/', views.MouvementCaisseCreateView.as_view(), name='mouvementcaisse_create'),

    # Suivi Recouvrement
    path('recouvrements/', views.RecouvrementListView.as_view(), name='recouvrement_list'),
    path('recouvrements/<int:pk>/modifier/', views.RecouvrementUpdateView.as_view(), name='recouvrement_update'),

    # Factures Fournisseurs (Achats)
    path('factures-fournisseurs/', views.FactureFournisseurListView.as_view(), name='facture_fournisseur_list'),
    path('factures-fournisseurs/ajouter/', views.FactureFournisseurCreateView.as_view(), name='facture_fournisseur_create'),
    path('factures-fournisseurs/paiement/ajouter/', views.PaiementCreateView.as_view(), name='paiement_create'),

    # Tableau de bord & Exports
    path('dashboard/', views.FinanceDashboardView.as_view(), name='dashboard'),
    path('export/ventes/', views.ExportVentesCSVView.as_view(), name='export_ventes'),
    path('export/achats/', views.ExportAchatsCSVView.as_view(), name='export_achats'),
]
