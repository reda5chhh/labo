"""
LABO.COS App — Vues de l'application core.

- CustomLoginView : connexion avec formulaire personnalisé et enregistrement AuditLog.
- CustomLogoutView : déconnexion avec confirmation.
- DashboardView : tableau de bord principal avec statistiques.
- ProfileView : gestion du profil utilisateur.
"""
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .forms import LaboCOSAuthenticationForm, UserProfileForm
from .models import User, AuditLog
from .mixins import LaboCOSLoginRequiredMixin


class CustomLoginView(LoginView):
    """
    Vue de connexion personnalisée.
    Utilise le formulaire Bootstrap 5 et redirige vers le dashboard.
    """
    form_class = LaboCOSAuthenticationForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        """Connexion réussie : message de bienvenue."""
        user = form.get_user()
        messages.success(
            self.request,
            _('Bienvenue, %(name)s ! Vous êtes connecté.') % {'name': user.nom_complet}
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """Connexion échouée : message d'avertissement."""
        messages.error(
            self.request,
            _('Identifiant ou mot de passe incorrect.')
        )
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    """Vue de déconnexion avec message de confirmation."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(
                request,
                _('Vous avez été déconnecté avec succès.')
            )
        return super().dispatch(request, *args, **kwargs)


class DashboardView(LaboCOSLoginRequiredMixin, TemplateView):
    """
    Tableau de bord principal de LABO.COS App.

    Affiche des statistiques générales :
    - Nombre de dossiers en cours
    - Devis en attente
    - Factures non soldées
    - Réceptions en attente de traitement
    - Dernières activités (AuditLog)
    """
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        """Injecter les statistiques dans le contexte du template."""
        context = super().get_context_data(**kwargs)

        # Import différé pour éviter les imports circulaires
        # Ces stats seront enrichies au fur et à mesure des phases
        stats = {
            'nb_dossiers': 0,
            'nb_devis_attente': 0,
            'nb_factures_non_soldees': 0,
            'nb_receptions_attente': 0,
        }

        # Tentative de récupération des stats réelles
        try:
            from apps.commercial.models import Dossier, Devis
            stats['nb_dossiers'] = Dossier.objects.filter(statut='EN_COURS').count()
            stats['nb_devis_attente'] = Devis.objects.filter(reception_bc=False).count()
        except Exception:
            pass

        try:
            from apps.finance.models import Facture
            stats['nb_factures_non_soldees'] = Facture.objects.exclude(
                statut_recouvrement='SOLDE'
            ).count()
        except Exception:
            pass

        try:
            from apps.technique.models import Reception
            stats['nb_receptions_attente'] = Reception.objects.filter(
                etat_essai='EN_ATTENTE'
            ).count()
        except Exception:
            pass

        context['stats'] = stats

        # Dernières activités (10 derniers AuditLogs de l'utilisateur courant)
        context['derniere_activite'] = AuditLog.objects.filter(
            user=self.request.user
        ).select_related('user').order_by('-timestamp')[:10]

        # Activité globale récente
        context['activite_globale'] = AuditLog.objects.select_related(
            'user'
        ).order_by('-timestamp')[:15]

        context['today'] = timezone.now()

        return context


class ProfileView(LaboCOSLoginRequiredMixin, UpdateView):
    """
    Vue de gestion du profil de l'utilisateur connecté.
    Permet de modifier prénom, nom, email, fonction et signature.
    """
    model = User
    form_class = UserProfileForm
    template_name = 'core/profile.html'
    success_url = reverse_lazy('core:profile')

    def get_object(self):
        """Retourne toujours l'utilisateur connecté."""
        return self.request.user

    def form_valid(self, form):
        messages.success(
            self.request,
            _('Votre profil a été mis à jour avec succès.')
        )
        return super().form_valid(form)


class SelectServiceView(LaboCOSLoginRequiredMixin, View):
    """
    Vue pour choisir un service après authentification.
    """
    def get(self, request, *args, **kwargs):
        services = [
            {
                'id': 'service_administratif',
                'nom': _('Service Administratif'),
                'icon': 'fa-building-columns',
                'color': 'primary',
                'description': _('Commercial et marchés, Facturation et comptabilité, Achats et logistique, Ressources Humaines'),
                'admin_only': False,
            },
            {
                'id': 'service_technique',
                'nom': _('Service Technique'),
                'icon': 'fa-microscope',
                'color': 'success',
                'description': _('Table des réceptions, Gestion laboratoire, Formation et qualification'),
                'admin_only': False,
            },
            {
                'id': 'service_qualite',
                'nom': _('Service Qualité'),
                'icon': 'fa-certificate',
                'color': 'warning',
                'description': _('Gestion documentaire, Fiche de progrès'),
                'admin_only': False,
            },
            {
                'id': 'service_metrologie',
                'nom': _('Service Métrologie et Matériel'),
                'icon': 'fa-ruler-combined',
                'color': 'info',
                'description': _('Inventaire, Fiche de vie, étalonnage, Capabilité, Paramètres'),
                'admin_only': False,
            },
            {
                'id': 'espace_user',
                'nom': _('Espace Utilisateur'),
                'icon': 'fa-user-gear',
                'color': 'secondary',
                'description': _('Congés, Attestations, Demande d\'achat, Spécimen signature'),
                'admin_only': False,
            },
            {
                'id': 'ged_archive',
                'nom': _('GED Archive'),
                'icon': 'fa-folder-open',
                'color': 'dark',
                'description': _('Archive, Services/Familles, Droits d\'accès'),
                'admin_only': False,
            },
            {
                'id': 'service_informatique',
                'nom': _('Service Informatique'),
                'icon': 'fa-laptop-code',
                'color': 'danger',
                'description': _('Suivi des modifications, Gestion des droits d\'accès, Données'),
                'admin_only': True,
            },
            {
                'id': 'parametrage',
                'nom': _('Paramétrage'),
                'icon': 'fa-gears',
                'color': 'teal',
                'description': _('Configuration générale et numérotations du laboratoire'),
                'admin_only': True,
            },
        ]
        
        # Filtrer selon les droits d'administration
        is_admin = request.user.est_admin or request.user.is_superuser
        if not is_admin:
            from apps.gestion_droits_acces.models import DroitAcces
            # Seuls les services où l'utilisateur a au moins un droit de voir actif
            allowed_services = set(DroitAcces.objects.filter(user=request.user, peut_voir=True).values_list('service', flat=True))
            allowed_services.add('espace_user') # Toujours accessible

            # Si le seul service autorisé est l'espace utilisateur, on redirige directement
            if len(allowed_services) == 1 and 'espace_user' in allowed_services:
                request.session['selected_service'] = 'espace_user'
                return redirect('core:dashboard')

            services = [s for s in services if s['id'] in allowed_services and not s['admin_only']]

        return render(request, 'core/select_service.html', {'services': services})

    def post(self, request, *args, **kwargs):
        service_id = request.POST.get('service')
        is_admin = request.user.est_admin or request.user.is_superuser
        if is_admin:
            valid_services = [
                'service_administratif', 'service_technique', 'service_qualite',
                'service_metrologie', 'espace_user', 'ged_archive',
                'service_informatique', 'parametrage'
            ]
        else:
            from apps.gestion_droits_acces.models import DroitAcces
            valid_services = list(DroitAcces.objects.filter(user=request.user, peut_voir=True).values_list('service', flat=True))
            valid_services.append('espace_user')

        if service_id in valid_services:
            request.session['selected_service'] = service_id
            messages.success(
                request,
                _('Vous avez accédé au : %s') % service_id.replace('_', ' ').title()
            )
            return redirect('core:dashboard')

        messages.error(request, _('Service invalide ou non autorisé.'))
        return redirect('core:select_service')


class GetEntityDataView(LoginRequiredMixin, View):
    """
    JSON API endpoint returning metadata for Clients, Devis, Dossiers, and Appels d'Offres.
    Used for AJAX dynamic autofill and cross-linking of form fields.
    """
    def get(self, request, entity_type, entity_id):
        from django.http import JsonResponse
        from django.shortcuts import get_object_or_404
        
        data = {}
        if entity_type == 'client':
            from apps.commercial.models import Client
            obj = get_object_or_404(Client, pk=entity_id)
            data = {
                'nom': obj.nom,
                'adresse': obj.adresse,
                'telephone': obj.telephone,
                'email': obj.email,
                'ice': obj.ice,
                'representant': obj.representant,
            }
        elif entity_type == 'devis':
            from apps.commercial.models import Devis
            obj = get_object_or_404(Devis, pk=entity_id)
            data = {
                'client_id': obj.client.pk if obj.client else None,
                'objet': obj.objet,
                'montant_ht': str(obj.montant_ht),
                'montant_ttc': str(obj.montant_ttc),
            }
        elif entity_type == 'dossier':
            from apps.commercial.models import Dossier
            obj = get_object_or_404(Dossier, pk=entity_id)
            data = {
                'client_id': obj.client.pk if obj.client else None,
                'nom_projet': obj.nom_projet,
            }
        elif entity_type == 'ao':
            from apps.marches.models import AOSoumission
            obj = get_object_or_404(AOSoumission, pk=entity_id)
            data = {
                'client_id': obj.client.pk if obj.client else None,
                'maitre_ouvrage': obj.client.nom if obj.client else '',
                'objet': obj.objet,
                'montant_soumission': str(obj.montant_soumission),
            }
        else:
            return JsonResponse({'error': 'Invalid entity type'}, status=400)
            
        return JsonResponse(data)

