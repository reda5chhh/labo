"""
LABO.COS App — Vues du service technique.

Gère les interfaces de création, modification, suppression, détail et liste
pour le module de gestion des réceptions d'échantillons.
"""
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)

from apps.core.mixins import ModulePermissionMixin
from .models import Reception
from .forms import ReceptionForm


# ============================================================
# Vues Réception d'échantillons
# ============================================================

class ReceptionListView(ModulePermissionMixin, ListView):
    model = Reception
    template_name = 'technique/reception_list.html'
    context_object_name = 'receptions'
    action_name = 'view'

    @property
    def module_name(self):
        tab = self.request.GET.get('tab')
        if tab == 'planning':
            return 'reception_planning'
        return 'reception_feuilles'

    def get_queryset(self):
        qs = Reception.objects.select_related('client', 'dossier', 'facture')

        # Filters
        client_id = self.request.GET.get('client')
        etat_essai = self.request.GET.get('etat_essai')
        etat_rapport = self.request.GET.get('etat_rapport')
        nature = self.request.GET.get('nature')
        date_du = self.request.GET.get('date_du')
        date_au = self.request.GET.get('date_au')

        if client_id:
            qs = qs.filter(client_id=client_id)
        if etat_essai:
            qs = qs.filter(etat_essai=etat_essai)
        if etat_rapport:
            qs = qs.filter(etat_rapport=etat_rapport)
        if nature:
            qs = qs.filter(nature_echantillon__icontains=nature)
        if date_du:
            qs = qs.filter(date_reception__gte=date_du)
        if date_au:
            qs = qs.filter(date_reception__lte=date_au)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.commercial.models import Client
        context['clients_list'] = Client.objects.filter(active=True).order_by('nom')
        context['etat_essai_choices'] = Reception.EtatEssai.choices
        context['etat_rapport_choices'] = Reception.EtatRapport.choices
        return context


class ReceptionDetailView(ModulePermissionMixin, DetailView):
    model = Reception
    template_name = 'technique/reception_detail.html'
    context_object_name = 'reception'
    module_name = 'reception_feuilles'
    action_name = 'view'


class ReceptionCreateView(ModulePermissionMixin, CreateView):
    model = Reception
    form_class = ReceptionForm
    template_name = 'technique/reception_form.html'
    success_url = reverse_lazy('technique:reception_list')
    module_name = 'reception_feuilles'
    action_name = 'add'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = _('Nouvelle Réception')
        context['action'] = _('Enregistrer')
        return context

    def form_valid(self, form):
        messages.success(self.request, _("La réception a été enregistrée avec succès."))
        return super().form_valid(form)


class ReceptionUpdateView(ModulePermissionMixin, UpdateView):
    model = Reception
    form_class = ReceptionForm
    template_name = 'technique/reception_form.html'
    success_url = reverse_lazy('technique:reception_list')
    module_name = 'reception_feuilles'
    action_name = 'edit'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = _('Modifier la Réception')
        context['action'] = _('Mettre à jour')
        return context

    def form_valid(self, form):
        messages.success(self.request, _("La réception a été mise à jour avec succès."))
        return super().form_valid(form)


class ReceptionDeleteView(ModulePermissionMixin, DeleteView):
    model = Reception
    template_name = 'technique/reception_confirm_delete.html'
    success_url = reverse_lazy('technique:reception_list')
    module_name = 'reception_feuilles'
    action_name = 'delete'

    def form_valid(self, form):
        messages.success(self.request, _("La réception a été supprimée."))
        return super().form_valid(form)

