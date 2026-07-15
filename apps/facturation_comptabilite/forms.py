"""Formulaires pour le module Finance de LABO.COS App."""
from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field

from .models import (
    Fournisseur, Facture, LigneFacture, Encaissement,
    FactureFournisseur, Paiement, MouvementCaisse, Recouvrement
)


class BaseLaboCOSForm(forms.ModelForm):
    """
    Formulaire de base configurant automatiquement Crispy Forms.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # Laisse le template rendre la balise <form>
        self.helper.disable_csrf = True  # Géré par le template {% csrf_token %}


class FournisseurForm(BaseLaboCOSForm):
    class Meta:
        model = Fournisseur
        exclude = ['created_by', 'updated_by']
        widgets = {
            'adresse': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Row(
                Column('nom', css_class='form-group col-md-8 mb-3'),
                Column('active', css_class='form-group col-md-4 mb-3 d-flex align-items-center pt-4'),
            ),
            Row(
                Column('ice', css_class='form-group col-md-3 mb-3'),
                Column('rc', css_class='form-group col-md-3 mb-3'),
                Column('if_fiscal', css_class='form-group col-md-3 mb-3'),
                Column('patente', css_class='form-group col-md-3 mb-3'),
            ),
            Row(
                Column('adresse', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('telephone', css_class='form-group col-md-6 mb-3'),
                Column('email', css_class='form-group col-md-6 mb-3'),
            ),
        )


class FactureForm(BaseLaboCOSForm):
    class Meta:
        model = Facture
        exclude = [
            'created_by', 'updated_by', 'statut',
            'envoye', 'envoye_par', 'date_envoi',
            'accuse', 'date_accuse',
            'reglement_recu', 'date_reglement',
            'validee_par_signature',
            'montant_ht', 'montant_tva', 'montant_ttc'
        ]
        widgets = {
            'date_facture': forms.DateInput(attrs={'type': 'date'}),
            'date_echeance': forms.DateInput(attrs={'type': 'date'}),
            'commentaire': forms.Textarea(attrs={'rows': 2}),
            'synthese_modification': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reference'].required = False
        self.fields['reference'].label = _("N° facture")
        self.helper.layout = Layout(
            Row(
                Column('reference', css_class='form-group col-md-3 mb-3'),
                Column('date_facture', css_class='form-group col-md-3 mb-3'),
                Column('bc', css_class='form-group col-md-2 mb-3'),
                Column('type_facture', css_class='form-group col-md-2 mb-3'),
                Column('delai', css_class='form-group col-md-1 mb-3'),
                Column('avec_ras', css_class='form-group col-md-1 mb-3'),
            ),
            Row(
                Column('client', css_class='form-group col-md-6 mb-3'),
                Column('dossier', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('projet', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('commentaire', css_class='form-group col-md-6 mb-3'),
                Column('synthese_modification', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('devis', css_class='form-group col-md-4 mb-3'),
                Column('decompte', css_class='form-group col-md-4 mb-3'),
                Column('difficulte_recouvrement', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('notes', css_class='form-group col-md-12 mb-3'),
            ),
        )


class LigneFactureForm(BaseLaboCOSForm):
    class Meta:
        model = LigneFacture
        fields = ['num_prix', 'designation', 'unite', 'quantite', 'prix_unitaire']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Row(
                Column('num_prix', css_class='form-group col-md-2 mb-2'),
                Column('designation', css_class='form-group col-md-4 mb-2'),
                Column('unite', css_class='form-group col-md-2 mb-2'),
                Column('quantite', css_class='form-group col-md-2 mb-2'),
                Column('prix_unitaire', css_class='form-group col-md-2 mb-2'),
            )
        )


class EncaissementForm(BaseLaboCOSForm):
    class Meta:
        model = Encaissement
        exclude = ['created_by', 'updated_by', 'reference']
        widgets = {
            'date_encaissement': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Row(
                Column('facture', css_class='form-group col-md-6 mb-3'),
                Column('date_encaissement', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('montant', css_class='form-group col-md-6 mb-3'),
                Column('moyen_paiement', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('reference_transaction', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('banque', css_class='form-group col-md-4 mb-3'),
                Column('compte_depot', css_class='form-group col-md-4 mb-3'),
                Column('encaisse', css_class='form-group col-md-4 mb-3 d-flex align-items-center pt-4'),
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        facture = cleaned_data.get('facture')
        montant = cleaned_data.get('montant')
        
        if facture and montant:
            solde = facture.solde
            # Si modification, ne pas compter l'ancien montant de cet encaissement dans le solde de la facture
            if self.instance and self.instance.pk:
                if self.instance.encaisse:
                    solde += self.instance.montant
            
            if montant > solde:
                self.add_error('montant', _(f"Le montant saisi ({montant} DH) dépasse le solde restant à payer sur cette facture ({solde} DH)."))
        return cleaned_data


class FactureFournisseurForm(BaseLaboCOSForm):
    class Meta:
        model = FactureFournisseur
        exclude = ['created_by', 'updated_by', 'reference_interne', 'statut']
        widgets = {
            'date_facture': forms.DateInput(attrs={'type': 'date'}),
            'date_echeance': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Row(
                Column('fournisseur', css_class='form-group col-md-6 mb-3'),
                Column('reference_fournisseur', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('date_facture', css_class='form-group col-md-6 mb-3'),
                Column('date_echeance', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('montant_ht', css_class='form-group col-md-4 mb-3'),
                Column('montant_tva', css_class='form-group col-md-4 mb-3'),
                Column('montant_ttc', css_class='form-group col-md-4 mb-3'),
            ),
        )


class PaiementForm(BaseLaboCOSForm):
    class Meta:
        model = Paiement
        exclude = ['created_by', 'updated_by', 'reference']
        widgets = {
            'date_paiement': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Row(
                Column('facture_fournisseur', css_class='form-group col-md-6 mb-3'),
                Column('date_paiement', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('montant', css_class='form-group col-md-6 mb-3'),
                Column('moyen_paiement', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('reference_transaction', css_class='form-group col-md-12 mb-3'),
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        ff = cleaned_data.get('facture_fournisseur')
        montant = cleaned_data.get('montant')
        
        if ff and montant:
            solde = ff.solde
            if self.instance and self.instance.pk:
                solde += self.instance.montant
            
            if montant > solde:
                self.add_error('montant', _(f"Le montant saisi ({montant} DH) dépasse le solde restant sur cette facture fournisseur ({solde} DH)."))
        return cleaned_data


class MouvementCaisseForm(BaseLaboCOSForm):
    class Meta:
        model = MouvementCaisse
        exclude = ['created_by', 'updated_by', 'reference', 'encaissement', 'paiement']
        widgets = {
            'date_mouvement': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Row(
                Column('date_mouvement', css_class='form-group col-md-6 mb-3'),
                Column('type_mouvement', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('montant', css_class='form-group col-md-4 mb-3'),
                Column('motif', css_class='form-group col-md-8 mb-3'),
            ),
        )


class RecouvrementForm(BaseLaboCOSForm):
    class Meta:
        model = Recouvrement
        exclude = ['created_by', 'updated_by', 'facture']
        widgets = {
            'dernier_rappel': forms.DateInput(attrs={'type': 'date'}),
            'commentaires': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Row(
                Column('statut_recouvrement', css_class='form-group col-md-6 mb-3'),
                Column('dernier_rappel', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('nombre_rappels', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('commentaires', css_class='form-group col-md-12 mb-3'),
            ),
        )
