"""Configuration de l'administration Django pour le module Finance."""
from django.contrib import admin
from .models import Fournisseur, Facture, Encaissement, FactureFournisseur, Paiement, MouvementCaisse, Recouvrement


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'telephone', 'email', 'active')
    search_fields = ('nom', 'ice', 'rc', 'if_fiscal')
    list_filter = ('active',)


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ('reference', 'client', 'date_facture', 'montant_ttc', 'statut', 'validee_par_signature')
    list_filter = ('statut', 'validee_par_signature', 'difficulte_recouvrement', 'date_facture')
    search_fields = ('reference', 'client__nom', 'devis__reference', 'dossier__reference')
    date_hierarchy = 'date_facture'


@admin.register(Encaissement)
class EncaissementAdmin(admin.ModelAdmin):
    list_display = ('reference', 'facture', 'date_encaissement', 'montant', 'moyen_paiement', 'encaisse')
    list_filter = ('moyen_paiement', 'encaisse', 'date_encaissement')
    search_fields = ('reference', 'reference_transaction', 'facture__reference', 'banque')
    date_hierarchy = 'date_encaissement'


@admin.register(FactureFournisseur)
class FactureFournisseurAdmin(admin.ModelAdmin):
    list_display = ('reference_interne', 'reference_fournisseur', 'fournisseur', 'date_facture', 'montant_ttc', 'statut')
    list_filter = ('statut', 'date_facture')
    search_fields = ('reference_interne', 'reference_fournisseur', 'fournisseur__nom')
    date_hierarchy = 'date_facture'


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('reference', 'facture_fournisseur', 'date_paiement', 'montant', 'moyen_paiement')
    list_filter = ('moyen_paiement', 'date_paiement')
    search_fields = ('reference', 'reference_transaction', 'facture_fournisseur__reference_interne')
    date_hierarchy = 'date_paiement'


@admin.register(MouvementCaisse)
class MouvementCaisseAdmin(admin.ModelAdmin):
    list_display = ('reference', 'date_mouvement', 'type_mouvement', 'montant', 'motif')
    list_filter = ('type_mouvement', 'date_mouvement')
    search_fields = ('reference', 'motif')
    date_hierarchy = 'date_mouvement'


@admin.register(Recouvrement)
class RecouvrementAdmin(admin.ModelAdmin):
    list_display = ('facture', 'statut_recouvrement', 'dernier_rappel', 'nombre_rappels')
    list_filter = ('statut_recouvrement', 'dernier_rappel')
    search_fields = ('facture__reference', 'facture__client__nom')
