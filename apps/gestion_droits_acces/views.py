"""
LABO.COS App — Vues de gestion des utilisateurs et des droits d'accès.
Accessible uniquement au superuser.
"""
from django.views.generic import ListView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.db.models import Prefetch

from apps.core.models import User
from .models import DroitAcces, SERVICE_CHOICES, MODULE_CHOICES
from .forms import UserCreateForm, UserUpdateForm


# ── Helper : accès superuser uniquement ───────────────────────────────────────

class SuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Réserve la vue aux superusers uniquement."""
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.est_admin

    def handle_no_permission(self):
        messages.error(self.request, _('Accès réservé aux administrateurs système.'))
        return redirect('core:dashboard')


# ── Gestion des Utilisateurs ─────────────────────────────────────────────────

class UserListView(SuperuserRequiredMixin, ListView):
    """Liste de tous les utilisateurs de l'application."""
    model = User
    template_name = 'gestion_droits_acces/user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.all().order_by('last_name', 'first_name')


class UserCreateView(SuperuserRequiredMixin, CreateView):
    """Créer un nouvel utilisateur."""
    model = User
    form_class = UserCreateForm
    template_name = 'gestion_droits_acces/user_form.html'
    success_url = reverse_lazy('gestion_droits_acces:user_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titre'] = _('Créer un utilisateur')
        ctx['action'] = _('Créer')
        return ctx

    def form_valid(self, form):
        messages.success(self.request, _('Utilisateur créé avec succès.'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _('Erreur dans le formulaire. Veuillez vérifier les champs.'))
        return super().form_invalid(form)


class UserUpdateView(SuperuserRequiredMixin, UpdateView):
    """Modifier un utilisateur existant."""
    model = User
    form_class = UserUpdateForm
    template_name = 'gestion_droits_acces/user_form.html'
    success_url = reverse_lazy('gestion_droits_acces:user_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titre'] = _('Modifier l\'utilisateur')
        ctx['action'] = _('Enregistrer')
        return ctx

    def form_valid(self, form):
        messages.success(self.request, _('Utilisateur mis à jour avec succès.'))
        return super().form_valid(form)


class UserToggleActiveView(SuperuserRequiredMixin, View):
    """Activer ou désactiver un compte utilisateur (POST)."""
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user == request.user:
            messages.error(request, _('Vous ne pouvez pas désactiver votre propre compte.'))
            return redirect('gestion_droits_acces:user_list')
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        status = _('activé') if user.is_active else _('désactivé')
        messages.success(request, _(f'Compte de {user.nom_complet} {status}.'))
        return redirect('gestion_droits_acces:user_list')


# ── Gestion des Droits d'Accès ────────────────────────────────────────────────

# Mapping service → liste de modules autorisés
SERVICE_MODULES = {
    'service_administratif': [
        'client', 'revue_demande', 'devis', 'dossier', 'convention', 'bon_livraison',
        'ao_soumission', 'ao_adjuge', 'caution', 'decompte', 'resultat_bc',
        'facture', 'encaissement', 'recouvrement', 'mouvement_caisse',
        'bci', 'demande_prix', 'prestataires_externes', 'bons_commandes', 'bons_reception', 'evaluation_prestataires', 'prestataires_agrees', 'cahier_charges',
        'personnel', 'conges_rh', 'attestations_rh', 'stagiaires', 'paie', 'qualification'
    ],
    'service_technique': [
        'reception_feuilles', 'reception_planning',
        'preparation_bleu', 'solution_lavante', 'suivi_balances', 'temperature_bassins', 'planning_maintenance_labo', 'fiche_maintenance', 'gestion_consommable', 'conditions_ambiantes', 'controle_eau',
        'fiche_qualification', 'feuilles_qualification'
    ],
    'service_qualite': [
        'suivi_docs', 'liste_suivi', 'revue_doc', 'veille_normative', 'controle_enreg', 'abbreviations',
        'fiche_progres'
    ],
    'service_metrologie': [
        'inventaire_materiel', 'fiche_vie', 'etalonnage_interne', 'maj_incertitude',
        'maj_elements_etalonner', 'maj_mouvement_materiel',
        'planning_etalonnage', 'planning_maintenance',
        'moyens_mesure', 'balances', 'exploitation_metrologique', 'verification_etuves',
        'donnees_balances', 'masses_etalons', 'donnees_materiel', 'periodicite',
        'instruction_etalonnage', 'type_intervention', 'accreditation'
    ],
    'espace_user':           ['conges', 'attestations', 'demandes_achat', 'specimen_signature'],
    'ged_archive':           ['archive_ged', 'services_familles_ged', 'droits_ged'],
    'service_informatique':  ['suivi_modifications', 'gestion_droits_acces', 'donnees_informatique'],
    'parametrage':           ['parametrage_general'],
}

MODULE_LABELS = dict(MODULE_CHOICES)
SERVICE_LABELS = dict(SERVICE_CHOICES)


class GestionDroitsView(SuperuserRequiredMixin, View):
    """
    Page principale de gestion des droits.
    Affiche la matrice des droits pour un utilisateur sélectionné.
    """
    template_name = 'gestion_droits_acces/droits_matrix.html'

    def get(self, request, *args, **kwargs):
        users = User.objects.all().order_by('last_name', 'first_name')
        selected_user_id = request.GET.get('user_id')
        selected_user = None
        matrix = []

        if selected_user_id:
            selected_user = get_object_or_404(User, pk=selected_user_id)
            # Récupérer tous les droits de cet utilisateur
            droits_qs = DroitAcces.objects.filter(user=selected_user)
            droits_map = {(d.service, d.module): d for d in droits_qs}

            for service_id, modules in SERVICE_MODULES.items():
                service_rows = []
                for module_id in modules:
                    key = (service_id, module_id)
                    droit = droits_map.get(key)
                    service_rows.append({
                        'module_id':    module_id,
                        'module_label': MODULE_LABELS.get(module_id, module_id),
                        'droit':        droit,
                        'droit_id':     droit.pk if droit else None,
                        'peut_voir':    droit.peut_voir    if droit else False,
                        'peut_ajouter': droit.peut_ajouter if droit else False,
                        'peut_modifier':droit.peut_modifier if droit else False,
                        'peut_annuler': droit.peut_annuler  if droit else False,
                    })
                matrix.append({
                    'service_id':    service_id,
                    'service_label': SERVICE_LABELS.get(service_id, service_id),
                    'modules':       service_rows,
                })

        return self._render(request, users, selected_user, matrix)

    def _render(self, request, users, selected_user, matrix):
        from django.shortcuts import render
        return render(request, self.template_name, {
            'users':         users,
            'selected_user': selected_user,
            'matrix':        matrix,
        })


class ToggleDroitView(SuperuserRequiredMixin, View):
    """
    Bascule une permission (POST AJAX).
    Crée le DroitAcces s'il n'existe pas encore.
    Retourne JSON {ok, nouvelle_valeur}.
    """
    def post(self, request, *args, **kwargs):
        user_id    = request.POST.get('user_id')
        service    = request.POST.get('service')
        module     = request.POST.get('module')
        permission = request.POST.get('permission')  # peut_voir | peut_ajouter | peut_modifier | peut_annuler

        ALLOWED = {'peut_voir', 'peut_ajouter', 'peut_modifier', 'peut_annuler'}
        if permission not in ALLOWED:
            return JsonResponse({'ok': False, 'error': 'Permission invalide'}, status=400)

        user = get_object_or_404(User, pk=user_id)
        droit, _ = DroitAcces.objects.get_or_create(
            user=user, service=service, module=module,
            defaults={'peut_voir': False, 'peut_ajouter': False, 'peut_modifier': False, 'peut_annuler': False}
        )
        # Basculer la valeur
        current = getattr(droit, permission)
        setattr(droit, permission, not current)
        droit.save(update_fields=[permission])

        return JsonResponse({'ok': True, 'value': not current})
