"""
LABO.COS App — Administration du module commercial.

Enregistre les modèles du module commercial dans le panel d'administration
Django avec filtres, recherche et personnalisation.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    Client, RevueDemande, Devis, Dossier, Convention,
    AOSoumission, AOAdjuge, Decompte, Caution,
    BonLivraison, DetailBonLivraison, ResultatBC
)


# ============================================================
# Inlines
# ============================================================

class DetailBonLivraisonInline(admin.TabularInline):
    model = DetailBonLivraison
    extra = 1
    fields = ['designation', 'quantite', 'observations']


# ============================================================
# Admin Classes
# ============================================================

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type_client', 'telephone', 'email', 'ice', 'active', 'created_at']
    list_filter = ['type_client', 'active', 'created_at']
    search_fields = ['nom', 'ice', 'rc', 'telephone', 'email']
    fieldsets = [
        (_('Raison Sociale & Type'), {'fields': ['nom', 'type_client', 'active']}),
        (_('Données Administratives'), {'fields': ['ice', 'rc', 'patente', 'if_fiscal']}),
        (_('Adresse & Coordonnées'), {'fields': ['adresse', 'telephone', 'email']}),
        (_('Contact Principal'), {'fields': ['contact_nom', 'contact_telephone', 'contact_email']}),
        (_('Comptabilité'), {'fields': ['solde_initial']}),
    ]


@admin.register(RevueDemande)
class RevueDemandeAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'date_demande', 'objet', 'statut', 'exigences_techniques', 'capacite_equipement', 'competence_personnel', 'delais_respectes']
    list_filter = ['statut', 'date_demande', 'exigences_techniques', 'capacite_equipement', 'competence_personnel', 'delais_respectes']
    search_fields = ['client__nom', 'objet', 'description']
    date_hierarchy = 'date_demande'


@admin.register(Devis)
class DevisAdmin(admin.ModelAdmin):
    list_display = ['reference', 'client', 'date_devis', 'objet', 'montant_ht', 'montant_ttc', 'statut']
    list_filter = ['statut', 'date_devis', 'taux_tva']
    search_fields = ['reference', 'client__nom', 'objet']
    readonly_fields = ['reference', 'montant_tva', 'montant_ttc']
    date_hierarchy = 'date_devis'


@admin.register(Dossier)
class DossierAdmin(admin.ModelAdmin):
    list_display = ['reference', 'client', 'nom_projet', 'date_ouverture', 'chef_projet', 'statut']
    list_filter = ['statut', 'date_ouverture', 'chef_projet']
    search_fields = ['reference', 'client__nom', 'nom_projet', 'emplacement']
    readonly_fields = ['reference']
    date_hierarchy = 'date_ouverture'


@admin.register(Convention)
class ConventionAdmin(admin.ModelAdmin):
    list_display = ['reference', 'client', 'objet', 'date_debut', 'date_fin', 'statut']
    list_filter = ['statut', 'date_debut', 'date_fin']
    search_fields = ['reference', 'client__nom', 'objet']
    readonly_fields = ['reference']
    date_hierarchy = 'date_debut'


@admin.register(AOSoumission)
class AOSoumissionAdmin(admin.ModelAdmin):
    list_display = ['reference_ao', 'client', 'objet', 'date_limite', 'montant_soumission', 'statut']
    list_filter = ['statut', 'date_limite']
    search_fields = ['reference_ao', 'client__nom', 'objet']
    date_hierarchy = 'date_limite'


@admin.register(AOAdjuge)
class AOAdjugeAdmin(admin.ModelAdmin):
    list_display = ['ao_soumission', 'date_adjudication', 'montant_final', 'caution_definitive_deposee', 'statut']
    list_filter = ['statut', 'date_adjudication', 'caution_definitive_deposee']
    search_fields = ['ao_soumission__reference_ao', 'ao_soumission__client__nom']
    date_hierarchy = 'date_adjudication'


@admin.register(Decompte)
class DecompteAdmin(admin.ModelAdmin):
    list_display = ['reference', 'dossier', 'numero_decompte', 'date_decompte', 'montant_ttc', 'statut']
    list_filter = ['statut', 'date_decompte']
    search_fields = ['reference', 'dossier__reference', 'dossier__client__nom']
    readonly_fields = ['reference']
    date_hierarchy = 'date_decompte'


@admin.register(Caution)
class CautionAdmin(admin.ModelAdmin):
    list_display = ['banque', 'type_caution', 'montant', 'date_depot', 'date_mainlevee', 'statut']
    list_filter = ['type_caution', 'statut', 'date_depot', 'banque']
    search_fields = ['banque', 'ao_soumission__reference_ao', 'ao_adjuge__ao_soumission__reference_ao']
    date_hierarchy = 'date_depot'


@admin.register(BonLivraison)
class BonLivraisonAdmin(admin.ModelAdmin):
    list_display = ['reference', 'dossier', 'date_bl', 'destinataire', 'statut']
    list_filter = ['statut', 'date_bl']
    search_fields = ['reference', 'dossier__reference', 'destinataire']
    readonly_fields = ['reference']
    inlines = [DetailBonLivraisonInline]
    date_hierarchy = 'date_bl'


@admin.register(ResultatBC)
class ResultatBCAdmin(admin.ModelAdmin):
    list_display = ['client', 'dossier', 'date_evaluation', 'note_satisfaction']
    list_filter = ['note_satisfaction', 'date_evaluation']
    search_fields = ['client__nom', 'dossier__reference', 'commentaires']
    date_hierarchy = 'date_evaluation'
