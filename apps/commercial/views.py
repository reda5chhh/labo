"""
LABO.COS App — Vues de l'application commercial.

Gère les interfaces de création, modification, suppression, détail et liste
pour toutes les entités du module commercial.
"""
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.forms import inlineformset_factory
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, TemplateView, View
)
from django.db.models import Q

from apps.core.mixins import ModulePermissionMixin
from .models import (
    Client, RevueDemande, Devis, Dossier, Convention,
    BonLivraison, DetailBonLivraison, DetailDevis
)
from .forms import (
    ClientForm, RevueDemandeForm, DevisForm, DossierForm, ConventionForm,
    BonLivraisonForm, DetailBonLivraisonForm, DetailDevisForm
)

# Formset en ligne pour Bon de Livraison et ses lignes de détail
DetailBonLivraisonFormSet = inlineformset_factory(
    BonLivraison,
    DetailBonLivraison,
    form=DetailBonLivraisonForm,
    extra=3,
    can_delete=True
)

# Formset en ligne pour Devis et ses lignes de détail
DetailDevisFormSet = inlineformset_factory(
    Devis,
    DetailDevis,
    form=DetailDevisForm,
    extra=0,
    can_delete=True
)


# ============================================================
# Vues génériques Annulation / Restauration (Soft Delete)
# ============================================================

class AnnulerView(ModulePermissionMixin, View):
    """
    Vue générique d'annulation (soft delete).
    Utilise model, success_url, et le message de succès définis dans la sous-classe.
    """
    model = None
    success_url = None
    module_name = 'commercial'
    action_name = 'delete'
    success_message = _('L\'enregistrement a été annulé.')

    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(self.model.objects_all, pk=kwargs['pk'])
        obj.delete()  # Soft delete via AuditableMixin
        messages.warning(request, self.success_message)
        return redirect(self.success_url)


class RestaurerView(ModulePermissionMixin, View):
    """
    Vue générique de restauration d'un enregistrement annulé.
    """
    model = None
    success_url = None
    module_name = 'commercial'
    action_name = 'delete'
    success_message = _('L\'enregistrement a été restauré.')

    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(self.model.objects_all, pk=kwargs['pk'])
        obj.restore()
        messages.success(request, self.success_message)
        return redirect(self.success_url)


# ============================================================
# Vues Client
# ============================================================

class ClientListView(ModulePermissionMixin, ListView):
    model = Client
    template_name = 'commercial/client_list.html'
    context_object_name = 'clients'
    module_name = 'client'
    action_name = 'view'

    def get_queryset(self):
        # Vérification si l'utilisateur a le droit d'annuler pour afficher les annulés
        has_cancel_perm = self.request.user.is_superuser or self.request.user.est_admin
        if not has_cancel_perm:
            from apps.gestion_droits_acces.models import DroitAcces
            has_cancel_perm = DroitAcces.objects.filter(
                user=self.request.user,
                module=self.module_name,
                peut_annuler=True
            ).exists()

        afficher_annules = self.request.GET.get('afficher_annules')
        if afficher_annules and has_cancel_perm:
            qs = Client.objects_all.filter(est_annule=True)
        else:
            qs = Client.objects.all()

        nom_contient = self.request.GET.get('nom_contient')
        nom_commence = self.request.GET.get('nom_commence')
        if nom_contient:
            qs = qs.filter(nom__icontains=nom_contient)
        if nom_commence:
            qs = qs.filter(nom__istartswith=nom_commence)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['afficher_annules'] = bool(self.request.GET.get('afficher_annules'))
        return context



class ClientCreateView(ModulePermissionMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'commercial/client_form.html'
    success_url = reverse_lazy('commercial:client_list')
    module_name = 'client'
    action_name = 'add'

    def form_valid(self, form):
        messages.success(self.request, _("Le client a été créé avec succès."))
        return super().form_valid(form)

class ClientUpdateView(ModulePermissionMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'commercial/client_form.html'
    success_url = reverse_lazy('commercial:client_list')
    module_name = 'client'
    action_name = 'edit'

    def form_valid(self, form):
        messages.success(self.request, _("Le client a été mis à jour avec succès."))
        return super().form_valid(form)


class ClientAnnulerView(AnnulerView):
    model = Client
    module_name = 'client'
    success_url = reverse_lazy('commercial:client_list')
    success_message = _('Le client a été annulé.')


class ClientRestaurerView(RestaurerView):
    model = Client
    module_name = 'client'
    success_url = reverse_lazy('commercial:client_list')
    success_message = _('Le client a été restauré.')


# ============================================================
# Vues Revue de la Demande
# ============================================================

class RevueDemandeListView(ModulePermissionMixin, ListView):
    model = RevueDemande
    template_name = 'commercial/revuedemande_list.html'
    context_object_name = 'revues'
    module_name = 'revue_demande'
    action_name = 'view'

    def get_queryset(self):
        has_cancel_perm = self.request.user.is_superuser or self.request.user.est_admin
        if not has_cancel_perm:
            from apps.gestion_droits_acces.models import DroitAcces
            has_cancel_perm = DroitAcces.objects.filter(
                user=self.request.user,
                module=self.module_name,
                peut_annuler=True
            ).exists()

        afficher_annules = self.request.GET.get('afficher_annules')
        if afficher_annules and has_cancel_perm:
            qs = RevueDemande.objects_all.filter(est_annule=True)
        else:
            qs = RevueDemande.objects.all()

        qs = qs.select_related('client', 'dossier')
        
        client_id = self.request.GET.get('client')
        ref = self.request.GET.get('ref')
        dossier_id = self.request.GET.get('dossier')
        date_du = self.request.GET.get('date_du')
        date_au = self.request.GET.get('date_au')
        accord_client = self.request.GET.get('accord_client')
        decision_labo = self.request.GET.get('decision_labo')
        
        if client_id:
            qs = qs.filter(client_id=client_id)
        if ref:
            qs = qs.filter(reference__icontains=ref)
        if dossier_id:
            qs = qs.filter(dossier_id=dossier_id)
        if date_du:
            qs = qs.filter(date_demande__gte=date_du)
        if date_au:
            qs = qs.filter(date_demande__lte=date_au)
        if accord_client:
            qs = qs.filter(accord_client=accord_client)
        if decision_labo:
            qs = qs.filter(decision_labo=decision_labo)
            
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clients_list'] = Client.objects.all().order_by('nom')
        context['dossiers_list'] = Dossier.objects.all().order_by('reference')
        context['devis_list'] = Devis.objects.select_related('client', 'revue_demande').all().order_by('-date_devis')
        context['afficher_annules'] = bool(self.request.GET.get('afficher_annules'))
        return context


class RevueDemandeCreateView(ModulePermissionMixin, CreateView):
    model = RevueDemande
    form_class = RevueDemandeForm
    template_name = 'commercial/revuedemande_form.html'
    success_url = reverse_lazy('commercial:revuedemande_list')
    module_name = 'revue_demande'
    action_name = 'add'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, _("La revue de demande a été enregistrée."))
        return super().form_valid(form)


class RevueDemandeUpdateView(ModulePermissionMixin, UpdateView):
    model = RevueDemande
    form_class = RevueDemandeForm
    template_name = 'commercial/revuedemande_form.html'
    success_url = reverse_lazy('commercial:revuedemande_list')
    module_name = 'revue_demande'
    action_name = 'edit'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, _("La revue de demande a été mise à jour."))
        return super().form_valid(form)


class RevueDemandePrintView(ModulePermissionMixin, DetailView):
    model = RevueDemande
    template_name = 'commercial/revuedemande_print.html'
    context_object_name = 'revue'
    module_name = 'revue_demande'
    action_name = 'view'


class RevueDemandeAnnulerView(AnnulerView):
    model = RevueDemande
    module_name = 'revue_demande'
    success_url = reverse_lazy('commercial:revuedemande_list')
    success_message = _('La revue de demande a été annulée.')


class RevueDemandeRestaurerView(RestaurerView):
    model = RevueDemande
    module_name = 'revue_demande'
    success_url = reverse_lazy('commercial:revuedemande_list')
    success_message = _('La revue de demande a été restaurée.')


# ============================================================
# Vues Devis
# ============================================================

class DevisListView(ModulePermissionMixin, ListView):
    model = Devis
    template_name = 'commercial/devis_list.html'
    context_object_name = 'devis_list'
    module_name = 'devis'
    action_name = 'view'

    def get_queryset(self):
        has_cancel_perm = self.request.user.is_superuser or self.request.user.est_admin
        if not has_cancel_perm:
            from apps.gestion_droits_acces.models import DroitAcces
            has_cancel_perm = DroitAcces.objects.filter(
                user=self.request.user,
                module=self.module_name,
                peut_annuler=True
            ).exists()

        afficher_annules = self.request.GET.get('afficher_annules')
        if afficher_annules and has_cancel_perm:
            queryset = Devis.objects_all.filter(est_annule=True)
        else:
            queryset = Devis.objects.all()

        queryset = queryset.select_related('client', 'revue_demande').prefetch_related('dossiers')
        
        # Filtres
        date_du = self.request.GET.get('date_du')
        date_au = self.request.GET.get('date_au')
        client_id = self.request.GET.get('client')
        dossier_id = self.request.GET.get('dossier')
        n_devis = self.request.GET.get('n_devis')
        statut_envoi = self.request.GET.get('statut_envoi', 'tous')
        statut_commande = self.request.GET.get('statut_commande', 'tous')

        if date_du:
            queryset = queryset.filter(date_devis__gte=date_du)
        if date_au:
            queryset = queryset.filter(date_devis__lte=date_au)
        if client_id and client_id != 'tous':
            queryset = queryset.filter(client_id=client_id)
        if dossier_id and dossier_id != 'tous':
            queryset = queryset.filter(dossiers__id=dossier_id)
        if n_devis:
            queryset = queryset.filter(reference__icontains=n_devis)
            
        if statut_envoi == 'envoye':
            queryset = queryset.filter(statut__in=['ENVOYE', 'ACCEPTE'])
        elif statut_envoi == 'non_envoye':
            queryset = queryset.exclude(statut__in=['ENVOYE', 'ACCEPTE'])
            
        if statut_commande == 'avec_bc':
            queryset = queryset.filter(reception_bc=True)
        elif statut_commande == 'sans_bc':
            queryset = queryset.filter(reception_bc=False)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.commercial.models import Client, Dossier
        context['clients'] = Client.objects.all().order_by('nom')
        context['dossiers'] = Dossier.objects.all().order_by('reference')
        context['afficher_annules'] = bool(self.request.GET.get('afficher_annules'))
        return context


class DevisDetailView(ModulePermissionMixin, DetailView):
    model = Devis
    template_name = 'commercial/devis_detail.html'
    context_object_name = 'devis'
    module_name = 'devis'
    action_name = 'view'


class DevisCreateView(ModulePermissionMixin, CreateView):
    model = Devis
    form_class = DevisForm
    template_name = 'commercial/devis_form.html'
    success_url = reverse_lazy('commercial:devis_list')
    module_name = 'devis'
    action_name = 'add'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = DetailDevisFormSet(self.request.POST)
        else:
            context['formset'] = DetailDevisFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, _("Le devis a été créé avec succès."))
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class AffecterDossierDevisView(ModulePermissionMixin, View):
    module_name = 'devis'
    action_name = 'edit'

    def post(self, request, *args, **kwargs):
        devis_id = request.POST.get('devis_id')
        dossier_id = request.POST.get('dossier_id')
        
        if not devis_id or not dossier_id:
            messages.error(request, _("Veuillez sélectionner un devis et un dossier."))
            return redirect('commercial:devis_list')
            
        try:
            from apps.commercial.models import Devis, Dossier
            devis = Devis.objects.get(pk=devis_id)
            dossier = Dossier.objects.get(pk=dossier_id)
            dossier.devis = devis
            dossier.save()
            messages.success(request, _("Le dossier %(dossier)s a été affecté au devis %(devis)s avec succès.") % {
                'dossier': dossier.reference,
                'devis': devis.reference
            })
        except (Devis.DoesNotExist, Dossier.DoesNotExist):
            messages.error(request, _("Devis ou Dossier introuvable."))
            
        return redirect('commercial:devis_list')


class DevisActionView(ModulePermissionMixin, View):
    module_name = 'devis'
    action_name = 'edit'

    def post(self, request, *args, **kwargs):
        devis_id = request.POST.get('devis_id')
        action_type = request.POST.get('action_type')
        
        if not devis_id:
            messages.error(request, _("Veuillez sélectionner un devis dans le tableau."))
            return redirect('commercial:devis_list')
            
        try:
            from apps.commercial.models import Devis
            devis = Devis.objects.get(pk=devis_id)
            
            if action_type == 'envoye':
                devis.statut = Devis.Statut.ENVOYE
                devis.save()
                messages.success(request, _("Le devis %(ref)s a été marqué comme envoyé.") % {'ref': devis.reference})
            elif action_type == 'signe':
                devis.statut = Devis.Statut.ACCEPTE
                devis.save()
                messages.success(request, _("Le devis %(ref)s a été signé et validé.") % {'ref': devis.reference})
            else:
                messages.warning(request, _("Action non reconnue."))
                
        except Devis.DoesNotExist:
            messages.error(request, _("Le devis sélectionné est introuvable."))
            
        return redirect('commercial:devis_list')


class DevisUpdateView(ModulePermissionMixin, UpdateView):
    model = Devis
    form_class = DevisForm
    template_name = 'commercial/devis_form.html'
    success_url = reverse_lazy('commercial:devis_list')
    module_name = 'devis'
    action_name = 'edit'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = DetailDevisFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = DetailDevisFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, _("Le devis a été mis à jour avec succès."))
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class DevisAnnulerView(AnnulerView):
    model = Devis
    module_name = 'devis'
    success_url = reverse_lazy('commercial:devis_list')
    success_message = _('Le devis a été annulé.')


class DevisRestaurerView(RestaurerView):
    model = Devis
    module_name = 'devis'
    success_url = reverse_lazy('commercial:devis_list')
    success_message = _('Le devis a été restauré.')


# ============================================================
# Vues Dossier
# ============================================================

class DossierListView(ModulePermissionMixin, ListView):
    model = Dossier
    template_name = 'commercial/dossier_list.html'
    context_object_name = 'dossiers'
    module_name = 'dossier'
    action_name = 'view'

    def get_queryset(self):
        has_cancel_perm = self.request.user.is_superuser or self.request.user.est_admin
        if not has_cancel_perm:
            from apps.gestion_droits_acces.models import DroitAcces
            has_cancel_perm = DroitAcces.objects.filter(
                user=self.request.user,
                module=self.module_name,
                peut_annuler=True
            ).exists()

        afficher_annules = self.request.GET.get('afficher_annules')
        if afficher_annules and has_cancel_perm:
            qs = Dossier.objects_all.filter(est_annule=True)
        else:
            qs = Dossier.objects.all()

        qs = qs.select_related('client', 'devis', 'chef_projet')
        
        # Filtres
        date_du = self.request.GET.get('date_du')
        date_au = self.request.GET.get('date_au')
        accreditation = self.request.GET.get('accreditation')
        client_id = self.request.GET.get('client')
        prestation = self.request.GET.get('prestation')
        etat_dossier = self.request.GET.get('etat_dossier')
        responsable_id = self.request.GET.get('responsable')
        num_dossier = self.request.GET.get('num_dossier')
        type_client = self.request.GET.get('type_client')
        
        if date_du:
            qs = qs.filter(date_ouverture__gte=date_du)
        if date_au:
            qs = qs.filter(date_ouverture__lte=date_au)
        if accreditation:
            qs = qs.filter(etat_accreditation=accreditation)
        if client_id:
            qs = qs.filter(client_id=client_id)
        if prestation:
            qs = qs.filter(prestation__icontains=prestation)
        if etat_dossier:
            qs = qs.filter(statut=etat_dossier)
        if responsable_id:
            qs = qs.filter(chef_projet_id=responsable_id)
        if num_dossier:
            qs = qs.filter(reference__icontains=num_dossier)
        if type_client:
            qs = qs.filter(client__type_client=type_client)
            
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        context['clients_list'] = Client.objects.all().order_by('nom')
        context['users_list'] = User.objects.all().order_by('username')
        context['type_client_choices'] = Client.ClientType.choices
        context['statut_choices'] = Dossier.Statut.choices
        context['afficher_annules'] = bool(self.request.GET.get('afficher_annules'))
        return context


class DossierDetailView(ModulePermissionMixin, DetailView):
    model = Dossier
    template_name = 'commercial/dossier_detail.html'
    context_object_name = 'dossier'
    module_name = 'dossier'
    action_name = 'view'


class DossierCreateView(ModulePermissionMixin, CreateView):
    model = Dossier
    form_class = DossierForm
    template_name = 'commercial/dossier_form.html'
    success_url = reverse_lazy('commercial:dossier_list')
    module_name = 'dossier'
    action_name = 'add'

    def form_valid(self, form):
        messages.success(self.request, _("Le dossier projet a été créé avec succès."))
        return super().form_valid(form)


class DossierUpdateView(ModulePermissionMixin, UpdateView):
    model = Dossier
    form_class = DossierForm
    template_name = 'commercial/dossier_form.html'
    success_url = reverse_lazy('commercial:dossier_list')
    module_name = 'dossier'
    action_name = 'edit'

    def form_valid(self, form):
        messages.success(self.request, _("Le dossier projet a été mis à jour avec succès."))
        return super().form_valid(form)


class DossierAnnulerView(AnnulerView):
    model = Dossier
    module_name = 'dossier'
    success_url = reverse_lazy('commercial:dossier_list')
    success_message = _('Le dossier a été annulé.')

class DossierRestaurerView(RestaurerView):
    model = Dossier
    module_name = 'dossier'
    success_url = reverse_lazy('commercial:dossier_list')
    success_message = _('Le dossier a été restauré.')


# ============================================================

class ConventionListView(ModulePermissionMixin, ListView):
    model = Convention
    template_name = 'commercial/convention_list.html'
    context_object_name = 'conventions'
    module_name = 'convention'
    action_name = 'view'

    def get_queryset(self):
        has_cancel_perm = self.request.user.is_superuser or self.request.user.est_admin
        if not has_cancel_perm:
            from apps.gestion_droits_acces.models import DroitAcces
            has_cancel_perm = DroitAcces.objects.filter(
                user=self.request.user,
                module=self.module_name,
                peut_annuler=True
            ).exists()

        afficher_annules = self.request.GET.get('afficher_annules')
        statut_annulation = self.request.GET.get('statut_annulation', 'en_cours')
        if (afficher_annules or statut_annulation == 'annule') and has_cancel_perm:
            qs = Convention.objects_all.filter(est_annule=True)
        else:
            qs = Convention.objects.all()

        # Date debut filters
        date_du = self.request.GET.get('date_du')
        date_au = self.request.GET.get('date_au')
        if date_du:
            qs = qs.filter(date_debut__gte=date_du)
        if date_au:
            qs = qs.filter(date_debut__lte=date_au)

        # N° Convention filter
        n_convention = self.request.GET.get('n_convention')
        if n_convention:
            qs = qs.filter(reference__icontains=n_convention)

        # Client filters
        client_id = self.request.GET.get('client_id')
        if client_id:
            qs = qs.filter(client_id=client_id)
        client_nom = self.request.GET.get('client_nom')
        if client_nom:
            qs = qs.filter(client__nom__icontains=client_nom)

        # Dossier filters
        dossier_id = self.request.GET.get('dossier_id')
        if dossier_id:
            from apps.commercial.models import Dossier
            try:
                dossier_obj = Dossier.objects.get(id=dossier_id)
                qs = qs.filter(client=dossier_obj.client)
            except Dossier.DoesNotExist:
                pass
        dossier_ref = self.request.GET.get('dossier_ref')
        if dossier_ref:
            qs = qs.filter(client__dossiers__reference__icontains=dossier_ref) | qs.filter(client__dossiers__nom_projet__icontains=dossier_ref)

        # Validée par client filter: tous/oui/non
        validee_par_client = self.request.GET.get('validee_par_client')
        if validee_par_client == 'oui':
            qs = qs.filter(validee_par_client=True)
        elif validee_par_client == 'non':
            qs = qs.filter(validee_par_client=False)

        return qs.select_related('client').distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.commercial.models import Client, Dossier
        context['clients_list'] = Client.objects.all()
        context['dossiers_list'] = Dossier.objects.all()
        context['afficher_annules'] = bool(self.request.GET.get('afficher_annules') or self.request.GET.get('statut_annulation') == 'annule')
        return context


class ConventionCreateView(ModulePermissionMixin, CreateView):
    model = Convention
    form_class = ConventionForm
    template_name = 'commercial/convention_form.html'
    success_url = reverse_lazy('commercial:convention_list')
    module_name = 'convention'
    action_name = 'add'

    def form_valid(self, form):
        messages.success(self.request, _("La convention a été enregistrée avec succès."))
        return super().form_valid(form)


class ConventionUpdateView(ModulePermissionMixin, UpdateView):
    model = Convention
    form_class = ConventionForm
    template_name = 'commercial/convention_form.html'
    success_url = reverse_lazy('commercial:convention_list')
    module_name = 'convention'
    action_name = 'edit'

    def form_valid(self, form):
        messages.success(self.request, _("La convention a été mise à jour."))
        return super().form_valid(form)


class ConventionDetailView(ModulePermissionMixin, DetailView):
    model = Convention
    template_name = 'commercial/convention_detail.html'
    context_object_name = 'convention'
    module_name = 'convention'
    action_name = 'view'


class ConventionAnnulerView(AnnulerView):
    model = Convention
    module_name = 'convention'
    success_url = reverse_lazy('commercial:convention_list')
    success_message = _('La convention a été annulée.')


class ConventionRestaurerView(RestaurerView):
    model = Convention
    module_name = 'convention'
    success_url = reverse_lazy('commercial:convention_list')
    success_message = _('La convention a été restaurée.')


class ConventionValiderView(ModulePermissionMixin, View):
    module_name = 'convention'
    action_name = 'modifier'

    def post(self, request, *args, **kwargs):
        convention_id = request.POST.get('convention_id')
        if convention_id:
            try:
                convention = Convention.objects.get(id=convention_id)
                convention.validee_par_client = True
                convention.save()
                from django.contrib import messages
                messages.success(request, _("La convention a été validée par le client avec succès."))
            except Convention.DoesNotExist:
                pass
        return redirect('commercial:convention_list')


# Vues de Marchés déplacées vers l'application marches



# ============================================================
# Vues Bons de Livraison (BL) avec Lignes d'articles
# ============================================================

class BLListView(ModulePermissionMixin, ListView):
    model = BonLivraison
    template_name = 'commercial/bl_list.html'
    context_object_name = 'bls'
    module_name = 'bon_livraison'
    action_name = 'view'

    def get_queryset(self):
        has_cancel_perm = self.request.user.is_superuser or self.request.user.est_admin
        if not has_cancel_perm:
            from apps.gestion_droits_acces.models import DroitAcces
            has_cancel_perm = DroitAcces.objects.filter(
                user=self.request.user,
                module=self.module_name,
                peut_annuler=True
            ).exists()

        afficher_annules = self.request.GET.get('afficher_annules')
        if afficher_annules and has_cancel_perm:
            qs = BonLivraison.objects_all.filter(est_annule=True)
        else:
            qs = BonLivraison.objects.all()

        qs = qs.select_related('dossier', 'dossier__client')

        # Apply advanced filters
        client_id = self.request.GET.get('client_id')
        if client_id:
            qs = qs.filter(dossier__client_id=client_id)

        recherche_txt = self.request.GET.get('recherche_txt')
        if recherche_txt:
            qs = qs.filter(
                Q(reference__icontains=recherche_txt) | 
                Q(destinataire__icontains=recherche_txt) | 
                Q(dossier__client__nom__icontains=recherche_txt)
            )

        dossier_id = self.request.GET.get('dossier_id')
        if dossier_id:
            qs = qs.filter(dossier_id=dossier_id)

        etat_dossier = self.request.GET.get('etat_dossier')
        if etat_dossier:
            qs = qs.filter(dossier__statut=etat_dossier)

        # Accuse Date range
        date_acc_du = self.request.GET.get('date_acc_du')
        date_acc_au = self.request.GET.get('date_acc_au')
        if date_acc_du:
            qs = qs.filter(date_accuse__gte=date_acc_du)
        if date_acc_au:
            qs = qs.filter(date_accuse__lte=date_acc_au)

        # Envoi Date range
        date_env_du = self.request.GET.get('date_env_du')
        date_env_au = self.request.GET.get('date_env_au')
        if date_env_du:
            qs = qs.filter(date_envoi__gte=date_env_du)
        if date_env_au:
            qs = qs.filter(date_envoi__lte=date_env_au)

        # Statut envoi
        statut_envoi = self.request.GET.get('statut_envoi')
        if statut_envoi == 'envoye':
            qs = qs.filter(envoye=True)
        elif statut_envoi == 'non_envoye':
            qs = qs.filter(envoye=False)

        # Statut accuse
        statut_accuse = self.request.GET.get('statut_accuse')
        if statut_accuse == 'accuse':
            qs = qs.filter(accuse=True)
        elif statut_accuse == 'non_accuse':
            qs = qs.filter(accuse=False)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['afficher_annules'] = bool(self.request.GET.get('afficher_annules'))
        
        # Load filter options
        from apps.commercial.models import Client, Dossier
        context['clients_list'] = Client.objects.all()
        context['dossiers_list'] = Dossier.objects.all()
        context['etat_dossier_choices'] = Dossier.Statut.choices
        return context


class BLDetailView(ModulePermissionMixin, DetailView):
    model = BonLivraison
    template_name = 'commercial/bl_detail.html'
    context_object_name = 'bl'
    module_name = 'bon_livraison'
    action_name = 'view'


class BLCreateView(ModulePermissionMixin, CreateView):
    model = BonLivraison
    form_class = BonLivraisonForm
    template_name = 'commercial/bl_form.html'
    success_url = reverse_lazy('commercial:bl_list')
    module_name = 'bon_livraison'
    action_name = 'add'

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user:
            initial['envoi_par'] = self.request.user.get_full_name() or self.request.user.username
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = DetailBonLivraisonFormSet(self.request.POST)
        else:
            context['formset'] = DetailBonLivraisonFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, _("Le Bon de Livraison a été créé avec succès."))
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class BLUpdateView(ModulePermissionMixin, UpdateView):
    model = BonLivraison
    form_class = BonLivraisonForm
    template_name = 'commercial/bl_form.html'
    success_url = reverse_lazy('commercial:bl_list')
    module_name = 'bon_livraison'
    action_name = 'edit'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = DetailBonLivraisonFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = DetailBonLivraisonFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, _("Le Bon de Livraison a été mis à jour avec succès."))
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class BLAnnulerView(AnnulerView):
    model = BonLivraison
    module_name = 'bon_livraison'
    success_url = reverse_lazy('commercial:bl_list')
    success_message = _('Le bon de livraison a été annulé.')


class BLRestaurerView(RestaurerView):
    model = BonLivraison
    module_name = 'bon_livraison'
    success_url = reverse_lazy('commercial:bl_list')
    success_message = _('Le bon de livraison a été restauré.')


# ResultatBC views déplacées vers l'application marches


# ============================================================
# Vues AJAX pour HTMX (Dropdowns en cascade)
# ============================================================
from django.http import HttpResponse

def ajax_load_devis(request):
    client_id = request.GET.get('client')
    if client_id:
        devis_list = Devis.objects.filter(client_id=client_id).order_by('-date_devis')
    else:
        devis_list = Devis.objects.none()
    
    html = '<option value="">---------</option>'
    for devis in devis_list:
        html += f'<option value="{devis.id}">{devis.reference} - {devis.objet[:30]} ({devis.montant_ttc} MAD)</option>'
    return HttpResponse(html)


def ajax_load_dossiers(request):
    client_id = request.GET.get('client')
    if client_id:
        dossiers_list = Dossier.objects.filter(client_id=client_id).order_by('-date_ouverture')
    else:
        dossiers_list = Dossier.objects.none()
        
    html = '<option value="">---------</option>'
    for d in dossiers_list:
        html += f'<option value="{d.id}">{d.reference} - {d.nom_projet[:30]}</option>'
    return HttpResponse(html)


def ajax_load_revues(request):
    client_id = request.GET.get('client')
    if client_id:
        revues_list = RevueDemande.objects.filter(client_id=client_id).order_by('-date_demande')
    else:
        revues_list = RevueDemande.objects.none()
        
    html = '<option value="">---------</option>'
    for r in revues_list:
        html += f'<option value="{r.id}">REV-{r.id} - {r.objet[:30]}</option>'
    return HttpResponse(html)


from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone

@login_required
@require_POST
def bl_mark_sent(request, pk):
    bl = get_object_or_404(BonLivraison, pk=pk)
    date_envoi = request.POST.get('date_envoi')
    envoi_par = request.POST.get('envoi_par')
    
    bl.envoye = True
    if date_envoi:
        bl.date_envoi = date_envoi
    else:
        bl.date_envoi = timezone.now().date()
    if envoi_par:
        bl.envoi_par = envoi_par
    bl.statut = BonLivraison.Statut.ENVOYE
    bl.save()
    
    messages.success(request, _("Le bon de livraison a été marqué comme envoyé."))
    return redirect('commercial:bl_list')


@login_required
@require_POST
def bl_toggle_accuse(request, pk):
    bl = get_object_or_404(BonLivraison, pk=pk)
    bl.accuse = not bl.accuse
    bl.save()
    messages.success(request, _("L'état de l'accusé de réception a été mis à jour."))
    return redirect('commercial:bl_list')


class BLDetailAjaxView(ModulePermissionMixin, ListView):
    model = DetailBonLivraison
    template_name = 'commercial/partials/bl_details.html'
    context_object_name = 'details'
    module_name = 'bon_livraison'
    action_name = 'view'

    def get_queryset(self):
        bl_id = self.request.GET.get('bl_id')
        if bl_id:
            return DetailBonLivraison.objects.filter(bon_livraison_id=bl_id)
        return DetailBonLivraison.objects.none()



