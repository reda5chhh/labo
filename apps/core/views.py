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
