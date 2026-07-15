from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column

from apps.marches.models import (
    AOSoumission, AOAdjuge, Decompte, Caution, ResultatBC
)

class BaseMarchesForm(forms.ModelForm):
    """
    Formulaire de base configurant automatiquement Crispy Forms
    et supprimant les boutons d'envoi par défaut pour laisser le template gérer.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # Laisse le template rendre la balise <form>
        self.helper.disable_csrf = True  # Géré par le template {% csrf_token %}


# ============================================================
# Formulaire AOSoumission
# ============================================================

class AOSoumissionForm(BaseMarchesForm):
    class Meta:
        model = AOSoumission
        exclude = ['created_by', 'updated_by']
        widgets = {
            'date_limite': forms.DateInput(attrs={'type': 'date'}),
            'heure_limite': forms.TimeInput(attrs={'type': 'time'}),
            'objet': forms.Textarea(attrs={'rows': 2}),
            'remarques': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Row(
                Column('ao_bc', css_class='form-group col-md-4 mb-3'),
                Column('reference_ao', css_class='form-group col-md-8 mb-3'),
            ),
            Row(
                Column('client', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('objet', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('lieu_execution', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('date_limite', css_class='form-group col-md-4 mb-3'),
                Column('heure_limite', css_class='form-group col-md-4 mb-3'),
                Column('reponse', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('statut_resultat', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('adjudicataire', css_class='form-group col-md-8 mb-3'),
                Column('montant', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('statut', css_class='form-group col-md-4 mb-3'),
                Column('estimation_initiale', css_class='form-group col-md-4 mb-3'),
                Column('montant_soumission', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('remarques', css_class='form-group col-md-12 mb-3'),
            ),
        )


# ============================================================
# Formulaire AOAdjuge
# ============================================================

class AOAdjugeForm(BaseMarchesForm):
    reste_a_encaisser = forms.DecimalField(
        label=_('reste à encaisser'),
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control-plaintext fw-bold text-danger'})
    )

    class Meta:
        model = AOAdjuge
        exclude = ['created_by', 'updated_by']
        widgets = {
            'date_adjudication': forms.DateInput(attrs={'type': 'date'}),
            'date_notification': forms.DateInput(attrs={'type': 'date'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'objet': forms.Textarea(attrs={'rows': 3}),
            'travaux_realises': forms.NumberInput(attrs={'step': '0.01'}),
            'reste_a_realiser': forms.NumberInput(attrs={'step': '0.01'}),
            'montant_final': forms.NumberInput(attrs={'step': '0.01'}),
            'montant_encaisse': forms.NumberInput(attrs={'step': '0.01'}),
            'acheve': forms.Select(choices=[(True, _('Oui')), (False, _('Non'))], attrs={'class': 'form-select'}),
            'solde': forms.Select(choices=[(True, _('Oui')), (False, _('Non'))], attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial['reste_a_encaisser'] = self.instance.reste_a_encaisser
        else:
            self.initial['reste_a_encaisser'] = 0.00

        self.helper.layout = Layout(
            Row(
                Column('ao_soumission', css_class='form-group col-md-6 mb-3'),
                Column('type_marche_bc', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('num_marche_bc', css_class='form-group col-md-6 mb-3'),
                Column('date_adjudication', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('client', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('objet', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('montant_final', css_class='form-group col-md-6 mb-3'),
                Column('date_notification', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('delai_realisation', css_class='form-group col-md-6 mb-3'),
                Column('travaux_realises', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('reste_a_realiser', css_class='form-group col-md-6 mb-3'),
                Column('montant_encaisse', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('reste_a_encaisser', css_class='form-group col-md-6 mb-3'),
                Column('statut', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('acheve', css_class='form-group col-md-4 mb-3'),
                Column('solde', css_class='form-group col-md-4 mb-3'),
                Column('caution_definitive_deposee', css_class='form-group col-md-4 mb-3 d-flex align-items-center pt-3'),
            ),
        )


# ============================================================
# Formulaire Decompte
# ============================================================

class DecompteForm(BaseMarchesForm):
    class Meta:
        model = Decompte
        fields = ['ao_adjuge', 'numero_decompte', 'date_decompte', 'montant_ttc', 'chemin_decompte', 'dossier', 'statut']
        widgets = {
            'date_decompte': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dossier'].required = False
        self.helper.layout = Layout(
            Row(
                Column('ao_adjuge', css_class='form-group col-md-6 mb-3'),
                Column('numero_decompte', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('date_decompte', css_class='form-group col-md-6 mb-3'),
                Column('montant_ttc', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('chemin_decompte', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('statut', css_class='form-group col-md-6 mb-3'),
                Column('dossier', css_class='form-group col-md-6 mb-3'),
            ),
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        from decimal import Decimal
        if instance.montant_ttc:
            instance.montant_ht = instance.montant_ttc / Decimal('1.20')
            instance.montant_tva = instance.montant_ttc - instance.montant_ht
        if commit:
            instance.save()
        return instance


# ============================================================
# Formulaire Caution
# ============================================================

class CautionForm(BaseMarchesForm):
    class Meta:
        model = Caution
        fields = [
            'numero_caution',
            'date_depot',
            'type_caution',
            'montant',
            'num_ao',
            'num_marche_bc',
            'client',
            'objet',
            'renvoyee_banque',
        ]
        widgets = {
            'date_depot': forms.DateInput(attrs={'type': 'date'}),
            'client': forms.Textarea(attrs={'rows': 3}),
            'objet': forms.Textarea(attrs={'rows': 3}),
            'renvoyee_banque': forms.Select(choices=[(True, _('Oui')), (False, _('Non'))]),
        }
        labels = {
            'numero_caution': _('Numéro caution'),
            'date_depot': _('Date caution'),
            'type_caution': _('Type caution'),
            'montant': _('Montant'),
            'num_ao': _('N° appel d\'offre'),
            'num_marche_bc': _('N° marché ou BC'),
            'client': _('client'),
            'objet': _('Objet'),
            'renvoyee_banque': _('Renvoyée à la banque'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Row(
                Column('numero_caution', css_class='form-group col-md-6 mb-3'),
                Column('date_depot', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('type_caution', css_class='form-group col-md-6 mb-3'),
                Column('montant', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('num_ao', css_class='form-group col-md-6 mb-3'),
                Column('num_marche_bc', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('client', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('objet', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('renvoyee_banque', css_class='form-group col-md-6 mb-3'),
            ),
        )


# ============================================================
# Formulaire ResultatBC
# ============================================================

class ResultatBCForm(BaseMarchesForm):
    class Meta:
        model = ResultatBC
        exclude = ['created_by', 'updated_by']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Row(
                Column('ao_soumission', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('nombre_participants', css_class='form-group col-md-6 mb-3'),
                Column('etat_reponse', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('entreprise_attributaire', css_class='form-group col-md-6 mb-3'),
                Column('montant', css_class='form-group col-md-6 mb-3'),
            ),
        )
