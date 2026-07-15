"""
LABO.COS App — Formulaires de l'application commercial.

Tous les formulaires utilisent django-crispy-forms pour un affichage
propre et moderne basé sur Bootstrap 5.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field, HTML

from .models import (
    Client, RevueDemande, Devis, Dossier, Convention,
    BonLivraison, DetailBonLivraison, DetailDevis
)


class BaseLaboCOSForm(forms.ModelForm):
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
# Formulaire Client
# ============================================================

class ClientForm(BaseLaboCOSForm):
    class Meta:
        model = Client
        exclude = ['created_by', 'updated_by', 'solde_initial', 'active']
        widgets = {
            'adresse': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Row(
                Column('nom', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('adresse', css_class='form-group col-md-8 mb-3'),
                Column('type_client', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('ville', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('representant', css_class='form-group col-md-8 mb-3'),
                Column('cin', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('telephone', css_class='form-group col-md-4 mb-3'),
                Column('gsm', css_class='form-group col-md-4 mb-3'),
                Column('fax', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('email', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('ice', css_class='form-group col-md-3 mb-3'),
                Column('rc', css_class='form-group col-md-3 mb-3'),
                Column('patente', css_class='form-group col-md-3 mb-3'),
                Column('if_fiscal', css_class='form-group col-md-3 mb-3'),
            ),
            Row(
                Column('synthese_modification', css_class='form-group col-md-12 mb-3'),
            ),
        )


# ============================================================
# Formulaire Revue de Demande
# ============================================================

class RevueDemandeForm(BaseLaboCOSForm):
    validation_technique = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label=_("Pour le service technique"),
        empty_label=_("Choisir un utilisateur...")
    )

    class Meta:
        model = RevueDemande
        exclude = [
            'created_by', 'updated_by',
            # Old fields replaced by the q1-q14 checklist — not shown in the form
            'exigences_techniques', 'capacite_equipement',
            'competence_personnel', 'delais_respectes',
            'description', 'remarques', 'statut',
            # Non-rendered fields that should use their defaults
            'decision_labo', 'accord_client',
        ]
        widgets = {
            'date_demande': forms.DateInput(attrs={'type': 'date'}),
            'validation_date': forms.DateInput(attrs={'type': 'date'}),
            'objet': forms.Textarea(attrs={'rows': 2}),
            'description': forms.Textarea(attrs={'rows': 2}),
            'objet_modification': forms.Textarea(attrs={'rows': 2}),
            'discussion_client': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        from django.contrib.auth import get_user_model
        from django.db.models import Q
        User = get_user_model()
        
        super().__init__(*args, **kwargs)
        
        # Set queryset for validation_technique
        self.fields['validation_technique'].queryset = User.objects.all().order_by('username')
        
        # Pre-select logged-in user if new form
        if not self.instance.pk and user:
            self.fields['validation_technique'].initial = user
        elif self.instance.pk and self.instance.validation_technique:
            # Find user matching the saved name
            saved_name = self.instance.validation_technique
            matched_user = User.objects.filter(
                Q(username=saved_name) | 
                Q(first_name__icontains=saved_name) | 
                Q(last_name__icontains=saved_name)
            ).first()
            if matched_user:
                self.fields['validation_technique'].initial = matched_user

        if 'reference' in self.fields:
            self.fields['reference'].disabled = True
            self.fields['reference'].required = False
            self.fields['reference'].widget.attrs['placeholder'] = 'N° automatique ...'
            
        self.fields['client'].widget.attrs.update({
            'hx-get': '/commercial/ajax/load-dossiers/',
            'hx-target': '#id_dossier',
            'hx-trigger': 'change'
        })
        self.helper.layout = Layout(
            # Partie Administrative
            HTML('<div class="alert alert-info py-2 mb-3 fw-bold text-center">Partie réservée au service administratif</div>'),
            Row(
                Column('date_demande', css_class='form-group col-md-4 mb-3'),
                Column('reference', css_class='form-group col-md-8 mb-3'),
            ),
            Row(
                Column('client', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('objet', css_class='form-group col-md-8 mb-3', label=_("Objet de la demande")),
                Column('ref_ao_bc', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('lieu_execution', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('type_reception_demande', css_class='form-group col-md-6 mb-3'),
                Column('nature_prestation', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('type_revue', css_class='form-group col-md-4 mb-3'),
                Column('etat_revue', css_class='form-group col-md-4 mb-3'),
                Column('ref_piece_jointe', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('objet_modification', css_class='form-group col-md-12 mb-3'),
            ),

            # Partie Technique
            HTML('<hr class="my-4"><div class="alert alert-warning py-2 mb-3 fw-bold text-center">Partie réservée au service technique</div>'),
            Row(
                # Colonne Gauche: Traitement de la demande (Checklist)
                Column(
                    HTML('<h6 class="fw-bold border-bottom pb-2 mb-3">Traitement de la demande</h6>'),
                    Row(Column('q1_exigences', css_class='col-md-4 mb-2'), Column('q1_note', css_class='col-md-8 mb-2')),
                    Row(Column('q2_methode', css_class='col-md-4 mb-2'), Column('q2_note', css_class='col-md-8 mb-2')),
                    Row(Column('q3_incertitudes', css_class='col-md-4 mb-2'), Column('q3_note', css_class='col-md-8 mb-2')),
                    Row(Column('q4_echantillonnage', css_class='col-md-4 mb-2'), Column('q4_note', css_class='col-md-8 mb-2')),
                    Row(Column('q5_acheminement', css_class='col-md-4 mb-2'), Column('q5_note', css_class='col-md-8 mb-2')),
                    Row(Column('q6_conservation', css_class='col-md-4 mb-2'), Column('q6_note', css_class='col-md-8 mb-2')),
                    Row(Column('q7_soustraitance', css_class='col-md-4 mb-2'), Column('q7_note', css_class='col-md-8 mb-2')),
                    Row(Column('q8_transmission', css_class='col-md-4 mb-2'), Column('q8_note', css_class='col-md-8 mb-2')),
                    Row(Column('q9_cooperation', css_class='col-md-4 mb-2'), Column('q9_note', css_class='col-md-8 mb-2')),
                    Row(Column('q10_avis', css_class='col-md-4 mb-2'), Column('q10_note', css_class='col-md-8 mb-2')),
                    Row(Column('q11_declaration', css_class='col-md-4 mb-2'), Column('q11_note', css_class='col-md-8 mb-2')),
                    Row(Column('q12_equipements', css_class='col-md-4 mb-2'), Column('q12_note', css_class='col-md-8 mb-2')),
                    Row(Column('q13_ressources', css_class='col-md-4 mb-2'), Column('q13_note', css_class='col-md-8 mb-2')),
                    Row(Column('q14_methodes_choisies', css_class='col-md-4 mb-2'), Column('q14_note', css_class='col-md-8 mb-2')),
                    css_class='col-lg-8'
                ),
                # Colonne Droite: Discussion, Sortie de revue, Validation
                Column(
                    HTML('<h6 class="fw-bold border-bottom pb-2 mb-3">Discussion</h6>'),
                    'discussion_client',
                    
                    HTML('<h6 class="fw-bold border-bottom pb-2 my-3">Eléments de sortie de revue</h6>'),
                    'sortie_resultat',
                    'sortie_decision',
                    'sortie_pieces_ref',
                    
                    HTML('<h6 class="fw-bold border-bottom pb-2 my-3">Validation et signature</h6>'),
                    'validation_date',
                    'validation_technique',
                    css_class='col-lg-4'
                ),
            )
        )

    def clean_validation_technique(self):
        user = self.cleaned_data.get('validation_technique')
        if user:
            return user.get_full_name() or user.username
        return ""


# ============================================================
# Formulaire Devis
# ============================================================

class DevisForm(BaseLaboCOSForm):
    class Meta:
        model = Devis
        exclude = ['created_by', 'updated_by', 'montant_ht', 'montant_tva', 'montant_ttc', 'reception_bc']
        widgets = {
            'date_devis': forms.DateInput(attrs={'type': 'date'}),
            'objet': forms.Textarea(attrs={'rows': 3, 'placeholder': 'PROJET'}),
            'synthese_modification': forms.TextInput(attrs={'placeholder': 'Syhthese de modification'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'reference' in self.fields:
            self.fields['reference'].disabled = True
            self.fields['reference'].required = False
            self.fields['reference'].widget.attrs['placeholder'] = 'N° automatique ...'
            
        self.fields['client'].widget.attrs.update({
            'hx-get': '/commercial/ajax/load-revues/',
            'hx-target': '#id_revue_demande',
            'hx-trigger': 'change'
        })
        self.helper.layout = Layout(
            Row(
                Column('reference', css_class='form-group col-md-4 mb-3'),
                Column('date_devis', css_class='form-group col-md-4 mb-3'),
                Column('client', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('objet', css_class='form-group col-md-8 mb-3'),
                Column('type_devis', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('taux_tva', css_class='form-group col-md-4 mb-3'),
                Column('validite_jours', css_class='form-group col-md-4 mb-3'),
                Column('statut', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('ref_bc', css_class='form-group col-md-4 mb-3'),
                Column('conditions_reglement', css_class='form-group col-md-4 mb-3'),
                Column('synthese_modification', css_class='form-group col-md-4 mb-3'),
            ),
        )


# ============================================================
# Formulaire Dossier
# ============================================================

class DossierForm(BaseLaboCOSForm):
    class Meta:
        model = Dossier
        exclude = ['created_by', 'updated_by']
        widgets = {
            'date_ouverture': forms.DateInput(attrs={'type': 'date'}),
            'date_cloture': forms.DateInput(attrs={'type': 'date'}),
            'date_os': forms.DateInput(attrs={'type': 'date'}),
            'nom_projet': forms.Textarea(attrs={'rows': 3, 'placeholder': 'PROJET'}),
            'commentaire': forms.Textarea(attrs={'rows': 3}),
            'synthese_modification': forms.TextInput(attrs={'placeholder': 'Syhthese de modification'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'reference' in self.fields:
            self.fields['reference'].disabled = True
            self.fields['reference'].required = False
            self.fields['reference'].widget.attrs['placeholder'] = 'N° automatique ...'
            
        self.fields['client'].widget.attrs.update({
            'hx-get': '/commercial/ajax/load-devis/',
            'hx-target': '#id_devis',
            'hx-trigger': 'change'
        })
        self.helper.layout = Layout(
            Row(
                Column('date_ouverture', css_class='form-group col-md-4 mb-3'),
                Column('etat_accreditation', css_class='form-group col-md-8 mb-3'),
            ),
            Row(
                Column('type_affaire', css_class='form-group col-md-6 mb-3'),
                Column('commande', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('reference', css_class='form-group col-md-6 mb-3'),
                Column('date_os', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('client', css_class='form-group col-md-6 mb-3'),
                Column('devis', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('entreprise', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('prestation', css_class='form-group col-md-6 mb-3'),
                Column('chef_projet', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('nom_projet', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('commentaire', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('statut', css_class='form-group col-md-6 mb-3'),
                Column('mode_reglement', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('delai_paiement', css_class='form-group col-md-6 mb-3'),
                Column('echeance_facturation', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('date_cloture', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('synthese_modification', css_class='form-group col-md-12 mb-3'),
            ),
        )


# ============================================================
# Formulaire Convention
# ============================================================

class ConventionForm(BaseLaboCOSForm):
    class Meta:
        model = Convention
        exclude = ['created_by', 'updated_by', 'reference']
        widgets = {
            'tarif_specifique': forms.Textarea(attrs={'rows': 3}),
            'date_debut': forms.DateInput(attrs={'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Row(
                Column('client', css_class='form-group col-md-6 mb-3'),
                Column('statut', css_class='form-group col-md-3 mb-3'),
                Column('validee_par_client', css_class='form-group col-md-3 mb-3'),
            ),
            Row(
                Column('objet', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('date_debut', css_class='form-group col-md-6 mb-3'),
                Column('date_fin', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('tarif_specifique', css_class='form-group col-md-12 mb-3'),
            ),
        )


# Formulaires de Marchés déplacés vers l'application marches


# ============================================================
# Formulaire BonLivraison
# ============================================================

class BonLivraisonForm(BaseLaboCOSForm):
    client_nom = forms.CharField(
        label=_('Client'),
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control-plaintext bg-light p-2 border rounded'}),
    )

    class Meta:
        model = BonLivraison
        exclude = ['created_by', 'updated_by', 'reference']
        widgets = {
            'date_bl': forms.DateInput(attrs={'type': 'date'}),
            'date_envoi': forms.DateInput(attrs={'type': 'date'}),
            'objet': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.dossier:
            if self.instance.dossier.client:
                self.fields['client_nom'].initial = self.instance.dossier.client.nom

        self.helper.layout = Layout(
            Row(
                Column('date_bl', css_class='form-group col-md-4 mb-3'),
                Column('dossier', css_class='form-group col-md-8 mb-3'),
            ),
            Row(
                Column('client_nom', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('objet', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('destinataire', css_class='form-group col-md-8 mb-3'),
                Column('statut', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('envoi_par', css_class='form-group col-md-8 mb-3'),
                Column('date_envoi', css_class='form-group col-md-4 mb-3'),
            ),
        )


# ============================================================
# Formulaire DetailBonLivraison
# ============================================================

class DetailBonLivraisonForm(BaseLaboCOSForm):
    class Meta:
        model = DetailBonLivraison
        fields = ['designation', 'quantite', 'observations']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Row(
                Column('designation', css_class='form-group col-md-6 mb-3'),
                Column('quantite', css_class='form-group col-md-2 mb-3'),
                Column('observations', css_class='form-group col-md-4 mb-3'),
            )
        )


# ResultatBCForm déplacé vers l'application marches


# ============================================================
# Formulaire DetailDevis
# ============================================================

class DetailDevisForm(BaseLaboCOSForm):
    class Meta:
        model = DetailDevis
        fields = ['num_prix', 'designation', 'unite', 'quantite', 'prix_unitaire']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Row(
                Column('num_prix', css_class='form-group col-md-2 mb-3'),
                Column('designation', css_class='form-group col-md-4 mb-3'),
                Column('unite', css_class='form-group col-md-2 mb-3'),
                Column('quantite', css_class='form-group col-md-2 mb-3'),
                Column('prix_unitaire', css_class='form-group col-md-2 mb-3'),
            )
        )
