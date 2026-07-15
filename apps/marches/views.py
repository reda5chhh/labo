from django.views.generic import TemplateView, CreateView, UpdateView, ListView
from django.views import View
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from apps.core.mixins import ModulePermissionMixin
from apps.marches.models import AOSoumission, AOAdjuge, Caution, Decompte, ResultatBC
from apps.marches.forms import AOSoumissionForm, AOAdjugeForm, CautionForm, DecompteForm, ResultatBCForm


class AOListView(ModulePermissionMixin, TemplateView):
    template_name = 'marches/ao_list.html'
    action_name = 'view'

    @property
    def module_name(self):
        tab = self.request.GET.get('tab')
        if tab == 'adjudications':
            return 'ao_adjuge'
        elif tab == 'cautions':
            return 'caution'
        elif tab == 'decomptes':
            return 'decompte'
        return 'ao_soumission'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        user = request.user
        is_admin_or_super = user.is_superuser or user.est_admin
        
        # Determine allowed modules for the user
        if is_admin_or_super:
            allowed_modules = ['ao_soumission', 'ao_adjuge', 'caution', 'decompte']
        else:
            from apps.gestion_droits_acces.models import DroitAcces
            from django.db.models import Q
            allowed_modules = list(DroitAcces.objects.filter(
                Q(peut_voir=True) | Q(peut_ajouter=True) | Q(peut_modifier=True) | Q(peut_annuler=True),
                user=user,
                module__in=['ao_soumission', 'ao_adjuge', 'caution', 'decompte']
            ).values_list('module', flat=True))

        # Priority list mapping modules to tabs
        priority_tabs = [
            ('ao_soumission', 'soumissions'),
            ('ao_adjuge', 'adjudications'),
            ('caution', 'cautions'),
            ('decompte', 'decomptes'),
        ]

        active_tab = request.GET.get('tab')
        
        # Determine which module corresponds to active_tab
        active_module = None
        if active_tab == 'adjudications':
            active_module = 'ao_adjuge'
        elif active_tab == 'cautions':
            active_module = 'caution'
        elif active_tab == 'decomptes':
            active_module = 'decompte'
        elif active_tab == 'soumissions' or not active_tab:
            active_module = 'ao_soumission'

        # If the user doesn't have permission for the requested tab, redirect to the first allowed tab
        if active_module not in allowed_modules:
            for module, tab in priority_tabs:
                if module in allowed_modules:
                    from django.shortcuts import redirect
                    from django.urls import reverse
                    url = reverse('marches:ao_list') + f'?tab={tab}'
                    return redirect(url)
            # If they have no permissions for any of these, let ModulePermissionMixin handle the 403
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user = self.request.user
        is_admin_or_super = user.is_superuser or user.est_admin
        if is_admin_or_super:
            can_view_soumissions = True
            can_view_adjudications = True
            can_view_cautions = True
            can_view_decomptes = True
        else:
            from apps.gestion_droits_acces.models import DroitAcces
            from django.db.models import Q
            allowed_modules = list(DroitAcces.objects.filter(
                Q(peut_voir=True) | Q(peut_ajouter=True) | Q(peut_modifier=True) | Q(peut_annuler=True),
                user=user,
                module__in=['ao_soumission', 'ao_adjuge', 'caution', 'decompte']
            ).values_list('module', flat=True))
            can_view_soumissions = 'ao_soumission' in allowed_modules
            can_view_adjudications = 'ao_adjuge' in allowed_modules
            can_view_cautions = 'caution' in allowed_modules
            can_view_decomptes = 'decompte' in allowed_modules

        context['can_view_soumissions'] = can_view_soumissions
        context['can_view_adjudications'] = can_view_adjudications
        context['can_view_cautions'] = can_view_cautions
        context['can_view_decomptes'] = can_view_decomptes

        # Check permissions to see cancelled records
        has_cancel_perm = is_admin_or_super
        if not has_cancel_perm:
            from apps.gestion_droits_acces.models import DroitAcces
            active_module = self.module_name
            has_cancel_perm = DroitAcces.objects.filter(
                user=user,
                module=active_module,
                peut_annuler=True
            ).exists()

        afficher_annules = self.request.GET.get('afficher_annules') == 'on'
        
        # 1. Soumissions filtering
        if can_view_soumissions:
            nom_acheteur = self.request.GET.get('nom_acheteur')
            manager_soumissions = AOSoumission.objects_all if (afficher_annules and has_cancel_perm) else AOSoumission.objects
            soumissions = manager_soumissions.select_related('client')
            if nom_acheteur:
                soumissions = soumissions.filter(client__nom__icontains=nom_acheteur)
            context['soumissions'] = soumissions
        else:
            context['soumissions'] = AOSoumission.objects.none()

        # 2. Adjudications filtering
        if can_view_adjudications:
            manager_adjudications = AOAdjuge.objects_all if (afficher_annules and has_cancel_perm) else AOAdjuge.objects
            adjudications = manager_adjudications.select_related('ao_soumission', 'ao_soumission__client', 'client')
            
            maitre_ouvrage = self.request.GET.get('maitre_ouvrage')
            if maitre_ouvrage:
                adjudications = adjudications.filter(
                    Q(ao_soumission__client__nom__icontains=maitre_ouvrage) |
                    Q(client__nom__icontains=maitre_ouvrage)
                )

            date_conv_du = self.request.GET.get('date_conv_du')
            date_conv_au = self.request.GET.get('date_conv_au')
            if date_conv_du:
                adjudications = adjudications.filter(date_adjudication__gte=date_conv_du)
            if date_conv_au:
                adjudications = adjudications.filter(date_adjudication__lte=date_conv_au)

            acheve = self.request.GET.get('acheve')
            if acheve == 'oui':
                adjudications = adjudications.filter(acheve=True)
            elif acheve == 'non':
                adjudications = adjudications.filter(acheve=False)

            solde = self.request.GET.get('solde')
            if solde == 'oui':
                adjudications = adjudications.filter(solde=True)
            elif solde == 'non':
                adjudications = adjudications.filter(solde=False)

            context['adjudications'] = adjudications
        else:
            context['adjudications'] = AOAdjuge.objects.none()

        # 3. Cautions filtering
        if can_view_cautions:
            manager_cautions = Caution.objects_all if (afficher_annules and has_cancel_perm) else Caution.objects
            cautions = manager_cautions.select_related('ao_soumission', 'ao_adjuge', 'ao_adjuge__ao_soumission')
            
            caution_du = self.request.GET.get('caution_du')
            caution_au = self.request.GET.get('caution_au')
            if caution_du:
                cautions = cautions.filter(date_depot__gte=caution_du)
            if caution_au:
                cautions = cautions.filter(date_depot__lte=caution_au)

            type_caution = self.request.GET.get('type_caution')
            if type_caution:
                cautions = cautions.filter(type_caution=type_caution)

            numero_caution = self.request.GET.get('numero_caution')
            if numero_caution:
                cautions = cautions.filter(numero_caution__icontains=numero_caution)

            client_caution = self.request.GET.get('client_caution')
            if client_caution:
                cautions = cautions.filter(
                    Q(ao_soumission__client__nom__icontains=client_caution) |
                    Q(ao_adjuge__ao_soumission__client__nom__icontains=client_caution)
                )

            context['cautions'] = cautions
        else:
            context['cautions'] = Caution.objects.none()
            
        # 4. Decomptes
        if can_view_decomptes:
            manager_decomptes = Decompte.objects_all if (afficher_annules and has_cancel_perm) else Decompte.objects
            context['decomptes'] = manager_decomptes.select_related('dossier', 'ao_adjuge', 'ao_adjuge__ao_soumission')
        else:
            context['decomptes'] = Decompte.objects.none()

        context['type_caution_choices'] = Caution.TypeCaution.choices
        context['afficher_annules'] = afficher_annules
        context['has_cancel_perm'] = has_cancel_perm
        return context


# AOSoumission CRUD
class AOSoumissionCreateView(ModulePermissionMixin, CreateView):
    model = AOSoumission
    form_class = AOSoumissionForm
    template_name = 'marches/ao_form.html'
    module_name = 'ao_soumission'
    action_name = 'add'

    def get_success_url(self):
        from django.urls import reverse
        tab = self.request.GET.get('tab') or 'soumissions'
        return reverse('marches:ao_list') + f'?tab={tab}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = _("Créer un Appel d'Offres (Soumission)")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Le dossier de soumission AO a été créé."))
        return super().form_valid(form)


class AOSoumissionUpdateView(ModulePermissionMixin, UpdateView):
    model = AOSoumission
    form_class = AOSoumissionForm
    template_name = 'marches/ao_form.html'
    module_name = 'ao_soumission'
    action_name = 'edit'

    def get_success_url(self):
        from django.urls import reverse
        tab = self.request.GET.get('tab') or 'soumissions'
        return reverse('marches:ao_list') + f'?tab={tab}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = _("Modifier la soumission AO")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Le dossier de soumission AO a été mis à jour."))
        return super().form_valid(form)


# AOAdjuge CRUD
class AOAdjugeCreateView(ModulePermissionMixin, CreateView):
    model = AOAdjuge
    form_class = AOAdjugeForm
    template_name = 'marches/ao_form.html'
    module_name = 'ao_adjuge'
    action_name = 'add'

    def get_success_url(self):
        from django.urls import reverse
        tab = self.request.GET.get('tab') or 'adjudications'
        return reverse('marches:ao_list') + f'?tab={tab}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = _("Enregistrer un Marché Adjugé / Notifié")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("L'adjudication du marché a été enregistrée."))
        return super().form_valid(form)


class AOAdjugeUpdateView(ModulePermissionMixin, UpdateView):
    model = AOAdjuge
    form_class = AOAdjugeForm
    template_name = 'marches/ao_form.html'
    module_name = 'ao_adjuge'
    action_name = 'edit'

    def get_success_url(self):
        from django.urls import reverse
        tab = self.request.GET.get('tab') or 'adjudications'
        return reverse('marches:ao_list') + f'?tab={tab}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = _("Modifier le Marché Adjugé")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Le marché adjugé a été mis à jour."))
        return super().form_valid(form)


# Caution CRUD
class CautionCreateView(ModulePermissionMixin, CreateView):
    model = Caution
    form_class = CautionForm
    template_name = 'marches/ao_form.html'
    module_name = 'caution'
    action_name = 'add'

    def get_success_url(self):
        from django.urls import reverse
        tab = self.request.GET.get('tab') or 'cautions'
        return reverse('marches:ao_list') + f'?tab={tab}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = _("Déposer une Caution Bancaire")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("La caution bancaire a été enregistrée."))
        return super().form_valid(form)


class CautionUpdateView(ModulePermissionMixin, UpdateView):
    model = Caution
    form_class = CautionForm
    template_name = 'marches/ao_form.html'
    module_name = 'caution'
    action_name = 'edit'

    def get_success_url(self):
        from django.urls import reverse
        tab = self.request.GET.get('tab') or 'cautions'
        return reverse('marches:ao_list') + f'?tab={tab}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = _("Modifier la Caution Bancaire")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("La caution bancaire a été mise à jour."))
        return super().form_valid(form)


# Decompte CRUD
class DecompteCreateView(ModulePermissionMixin, CreateView):
    model = Decompte
    form_class = DecompteForm
    template_name = 'marches/ao_form.html'
    module_name = 'decompte'
    action_name = 'add'

    def get_initial(self):
        initial = super().get_initial()
        ao_adjuge_id = self.request.GET.get('ao_adjuge_id')
        if ao_adjuge_id:
            initial['ao_adjuge'] = ao_adjuge_id
        return initial

    def get_success_url(self):
        from django.urls import reverse
        tab = self.request.GET.get('tab') or 'decomptes'
        return reverse('marches:ao_list') + f'?tab={tab}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = _("Créer une situation / Décompte de travaux")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Le décompte a été créé."))
        return super().form_valid(form)


class DecompteUpdateView(ModulePermissionMixin, UpdateView):
    model = Decompte
    form_class = DecompteForm
    template_name = 'marches/ao_form.html'
    module_name = 'decompte'
    action_name = 'edit'

    def get_success_url(self):
        from django.urls import reverse
        tab = self.request.GET.get('tab') or 'decomptes'
        return reverse('marches:ao_list') + f'?tab={tab}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = _("Modifier le décompte")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Le décompte a été mis à jour."))
        return super().form_valid(form)


# Vues Résultats / Enquêtes Satisfaction
class ResultatBCListView(ModulePermissionMixin, ListView):
    model = ResultatBC
    template_name = 'marches/resultatbc_list.html'
    context_object_name = 'soumissions'
    module_name = 'resultat_bc'
    action_name = 'view'

    def get_queryset(self):
        qs = AOSoumission.objects.select_related('client', 'resultat')
        
        # Apply filters
        date_du = self.request.GET.get('date_du')
        date_au = self.request.GET.get('date_au')
        if date_du:
            qs = qs.filter(date_limite__date__gte=date_du)
        if date_au:
            qs = qs.filter(date_limite__date__lte=date_au)

        ref_ao = self.request.GET.get('ref_ao')
        if ref_ao:
            qs = qs.filter(reference_ao__icontains=ref_ao)

        etat_reponse = self.request.GET.get('etat_reponse')
        if etat_reponse and etat_reponse != 'tous':
            if etat_reponse == 'NON_ATTRIBUE':
                qs = qs.filter(Q(resultat__isnull=True) | Q(resultat__etat_reponse='NON_ATTRIBUE'))
            else:
                qs = qs.filter(resultat__etat_reponse=etat_reponse)

        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['etat_reponse_choices'] = ResultatBC.EtatReponse.choices
        return context


class ResultatBCValiderView(ModulePermissionMixin, View):
    module_name = 'resultat_bc'
    action_name = 'add'

    def post(self, request, *args, **kwargs):
        ao_id = request.POST.get('ao_id')
        if ao_id:
            try:
                ao = AOSoumission.objects.get(id=ao_id)
                resultat, created = ResultatBC.objects.get_or_create(ao_soumission=ao)
                
                nombre_participants = request.POST.get('nombre_participants', 0)
                entreprise_attributaire = request.POST.get('entreprise_attributaire', '')
                montant = request.POST.get('montant', 0.00)
                etat_reponse = request.POST.get('etat_reponse', 'NON_ATTRIBUE')
                
                resultat.nombre_participants = int(nombre_participants) if nombre_participants else 0
                resultat.entreprise_attributaire = entreprise_attributaire
                resultat.montant = float(montant) if montant else 0.00
                resultat.etat_reponse = etat_reponse
                resultat.save()

                if etat_reponse == 'ADJUGE':
                    ao.statut = AOSoumission.Statut.ADJUGE
                    from apps.marches.models import AOAdjuge
                    if not hasattr(ao, 'adjudication'):
                        AOAdjuge.objects.create(
                            ao_soumission=ao,
                            montant_final=resultat.montant
                        )
                elif etat_reponse == 'REJETE':
                    ao.statut = AOSoumission.Statut.REJETE
                else:
                    ao.statut = AOSoumission.Statut.SOUMIS
                ao.save()

                messages.success(request, _("Le résultat de l'attribution a été enregistré avec succès."))
            except (AOSoumission.DoesNotExist, ValueError) as e:
                messages.error(request, _("Erreur lors de l'enregistrement : ") + str(e))
        return redirect('marches:resultatbc_list')


class DecompteDetailAjaxView(ModulePermissionMixin, ListView):
    model = Decompte
    template_name = 'marches/partials/decompte_details.html'
    context_object_name = 'decomptes'
    module_name = 'decompte'
    action_name = 'view'

    def get_queryset(self):
        # We also need to support displaying cancelled/deleted decomptes inside the master-detail list if desired
        afficher_annules = self.request.GET.get('afficher_annules') == 'on' or 'tab' in self.request.GET
        manager = Decompte.objects_all if (self.request.user.is_superuser or self.request.user.est_admin) else Decompte.objects
        ao_adjuge_id = self.request.GET.get('ao_adjuge_id')
        if ao_adjuge_id:
            return manager.filter(ao_adjuge_id=ao_adjuge_id).select_related('dossier')
        return manager.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        has_cancel_perm = self.request.user.is_superuser or self.request.user.est_admin
        if not has_cancel_perm:
            from apps.gestion_droits_acces.models import DroitAcces
            has_cancel_perm = DroitAcces.objects.filter(
                user=self.request.user,
                module=self.module_name,
                peut_annuler=True
            ).exists()
        context['has_cancel_perm'] = has_cancel_perm
        return context


# Generic views for cancel/restore in marches app
class MarchesAnnulerView(ModulePermissionMixin, View):
    model = None
    success_url = None
    module_name = 'marches'
    action_name = 'delete'
    success_message = _("L'enregistrement a été annulé.")

    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(self.model.objects_all, pk=kwargs['pk'])
        obj.delete()
        messages.warning(request, self.success_message)
        tab = request.GET.get('tab') or request.POST.get('tab')
        url = self.success_url
        if tab:
            url += f'?tab={tab}'
        return redirect(url)


class MarchesRestaurerView(ModulePermissionMixin, View):
    model = None
    success_url = None
    module_name = 'marches'
    action_name = 'delete'
    success_message = _("L'enregistrement a été restauré.")

    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(self.model.objects_all, pk=kwargs['pk'])
        obj.restore()
        messages.success(request, self.success_message)
        tab = request.GET.get('tab') or request.POST.get('tab')
        url = self.success_url
        if tab:
            url += f'?tab={tab}'
        return redirect(url)


class AOSoumissionAnnulerView(MarchesAnnulerView):
    model = AOSoumission
    module_name = 'ao_soumission'
    success_url = reverse_lazy('marches:ao_list')
    success_message = _("Le dossier de soumission AO a été annulé.")


class AOSoumissionRestaurerView(MarchesRestaurerView):
    model = AOSoumission
    module_name = 'ao_soumission'
    success_url = reverse_lazy('marches:ao_list')
    success_message = _("Le dossier de soumission AO a été restauré.")


class AOAdjugeAnnulerView(MarchesAnnulerView):
    model = AOAdjuge
    module_name = 'ao_adjuge'
    success_url = reverse_lazy('marches:ao_list')
    success_message = _("Le marché adjugé a été annulé.")


class AOAdjugeRestaurerView(MarchesRestaurerView):
    model = AOAdjuge
    module_name = 'ao_adjuge'
    success_url = reverse_lazy('marches:ao_list')
    success_message = _("Le marché adjugé a été restauré.")


class CautionAnnulerView(MarchesAnnulerView):
    model = Caution
    module_name = 'caution'
    success_url = reverse_lazy('marches:ao_list')
    success_message = _("La caution bancaire a été annulée.")


class CautionRestaurerView(MarchesRestaurerView):
    model = Caution
    module_name = 'caution'
    success_url = reverse_lazy('marches:ao_list')
    success_message = _("La caution bancaire a été restaurée.")


class DecompteAnnulerView(MarchesAnnulerView):
    model = Decompte
    module_name = 'decompte'
    success_url = reverse_lazy('marches:ao_list')
    success_message = _("Le décompte a été annulé.")


class DecompteRestaurerView(MarchesRestaurerView):
    model = Decompte
    module_name = 'decompte'
    success_url = reverse_lazy('marches:ao_list')
    success_message = _("Le décompte a été restauré.")
