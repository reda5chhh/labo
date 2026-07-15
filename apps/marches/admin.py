from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    AOSoumission, AOAdjuge, Decompte, Caution, ResultatBC
)


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


@admin.register(ResultatBC)
class ResultatBCAdmin(admin.ModelAdmin):
    list_display = ['ao_soumission', 'nombre_participants', 'entreprise_attributaire', 'montant', 'etat_reponse']
    list_filter = ['etat_reponse']
    search_fields = ['ao_soumission__reference_ao', 'entreprise_attributaire']
