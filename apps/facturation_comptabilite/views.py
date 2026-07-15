"""Vues pour le module Finance (Facturation, Encaissements, Caisse, Fournisseurs) de LABO.COS App."""
import csv
import datetime
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, TemplateView
)
from django.db.models import Sum, Q

from apps.core.mixins import ModulePermissionMixin
from apps.table_receptions.models import Reception
from apps.commercial.models import Devis
from .models import (
    Fournisseur, Facture, LigneFacture, Encaissement,
    FactureFournisseur, Paiement, MouvementCaisse, Recouvrement
)
from .forms import (
    FournisseurForm, FactureForm, LigneFactureForm, EncaissementForm,
    FactureFournisseurForm, PaiementForm, MouvementCaisseForm, RecouvrementForm
)


# ============================================================
# 1. Vues Fournisseur
# ============================================================

class FournisseurListView(ModulePermissionMixin, ListView):
    model = Fournisseur
    template_name = 'finance/fournisseur_list.html'
    context_object_name = 'fournisseurs'
    module_name = 'finance'
    action_name = 'view'


class FournisseurCreateView(ModulePermissionMixin, CreateView):
    model = Fournisseur
    form_class = FournisseurForm
    template_name = 'finance/fournisseur_form.html'
    success_url = reverse_lazy('finance:fournisseur_list')
    module_name = 'finance'
    action_name = 'add'

    def form_valid(self, form):
        messages.success(self.request, _("Le fournisseur a été créé avec succès."))
        return super().form_valid(form)


class FournisseurUpdateView(ModulePermissionMixin, UpdateView):
    model = Fournisseur
    form_class = FournisseurForm
    template_name = 'finance/fournisseur_form.html'
    success_url = reverse_lazy('finance:fournisseur_list')
    module_name = 'finance'
    action_name = 'change'

    def form_valid(self, form):
        messages.success(self.request, _("Le fournisseur a été mis à jour avec succès."))
        return super().form_valid(form)


# ============================================================
# 2. Vues Facture Client (Facturation)
# ============================================================

class FactureListView(ModulePermissionMixin, ListView):
    model = Facture
    template_name = 'finance/facture_list.html'
    context_object_name = 'factures'
    module_name = 'finance'
    action_name = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Sélection de la facture pour afficher les détails en bas de la page
        selected_id = self.request.GET.get('selected')
        selected_facture = None
        if selected_id:
            try:
                selected_facture = Facture.objects.get(id=selected_id)
            except Facture.DoesNotExist:
                pass
        
        if not selected_facture and context['factures'].exists():
            selected_facture = context['factures'].first()
            
        context['selected_facture'] = selected_facture
        return context


class FactureDetailView(ModulePermissionMixin, DetailView):
    model = Facture
    template_name = 'finance/facture_detail.html'
    context_object_name = 'facture'
    module_name = 'finance'
    action_name = 'view'


class FactureCreateView(ModulePermissionMixin, CreateView):
    model = Facture
    form_class = FactureForm
    template_name = 'finance/facture_form.html'
    module_name = 'finance'
    action_name = 'add'

    def form_valid(self, form):
        messages.success(self.request, _("La facture a été créée en tant que brouillon. Vous pouvez maintenant ajouter des lignes."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('finance:facture_update', kwargs={'pk': self.object.pk})


class FactureUpdateView(ModulePermissionMixin, UpdateView):
    model = Facture
    form_class = FactureForm
    template_name = 'finance/facture_form.html'
    module_name = 'finance'
    action_name = 'change'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lignes'] = self.object.lignes.all()
        context['line_form'] = LigneFactureForm()
        context['all_devis'] = Devis.objects.filter(client=self.object.client, statut='ACCEPTE')
        context['all_factures'] = Facture.objects.filter(client=self.object.client).exclude(id=self.object.id)
        return context

    def form_valid(self, form):
        messages.success(self.request, _("La facture a été mise à jour."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('finance:facture_list')


class FactureSignView(ModulePermissionMixin, View):
    """Signe et valide officiellement la facture (empreinte digitale)."""
    module_name = 'finance'
    action_name = 'change'

    def post(self, request, pk, *args, **kwargs):
        facture = get_object_or_404(Facture, pk=pk)
        if not facture.validee_par_signature:
            facture.validee_par_signature = True
            facture.statut = Facture.StatutFacture.VALIDEE
            facture.save()
            # Créer aussi le dossier de recouvrement associé
            Recouvrement.objects.get_or_create(facture=facture)
            messages.success(request, _(f"La facture {facture.reference} a été officiellement signée et validée."))
        return redirect('finance:facture_list')


class FactureUpdateRecouvrementView(ModulePermissionMixin, View):
    """Mise à jour de la difficulté de recouvrement de la facture."""
    module_name = 'finance'
    action_name = 'change'

    def post(self, request, pk, *args, **kwargs):
        facture = get_object_or_404(Facture, pk=pk)
        difficulte = request.POST.get('difficulte')
        if difficulte in Facture.DifficulteRecouvrement.values:
            facture.difficulte_recouvrement = difficulte
            facture.save()
            messages.success(request, _("Le statut de recouvrement de la facture a été mis à jour."))
        return redirect('finance:facture_list')


# ============================================================
# 3. Facturation Réception (Sélection et facturation de masse)
# ============================================================

class FactureReceptionListView(ModulePermissionMixin, ListView):
    model = Reception
    template_name = 'finance/facture_reception_list.html'
    context_object_name = 'receptions'
    module_name = 'finance'
    action_name = 'view'

    def get_queryset(self):
        # Lister uniquement les réceptions dont le rapport est validé et non encore facturées
        return Reception.objects.filter(facture__isnull=True)


class FactureGroupedCreateView(ModulePermissionMixin, View):
    """Génère une facture groupée pour un client à partir de réceptions sélectionnées."""
    module_name = 'finance'
    action_name = 'add'

    def post(self, request, *args, **kwargs):
        reception_ids = request.POST.getlist('receptions')
        if not reception_ids:
            messages.error(request, _("Veuillez sélectionner au moins une réception à facturer."))
            return redirect('finance:facture_reception_list')

        receptions = Reception.objects.filter(id__in=reception_ids, facture__isnull=True)
        if not receptions.exists():
            messages.error(request, _("Aucune réception valide trouvée."))
            return redirect('finance:facture_reception_list')

        # Regrouper par client (toutes les réceptions doivent appartenir au même client)
        client = receptions.first().client
        if any(r.client != client for r in receptions):
            messages.error(request, _("Toutes les réceptions sélectionnées doivent appartenir au même client."))
            return redirect('finance:facture_reception_list')

        # Calculer le montant HT total estimé (ex: 1200 DH par réception d'essais)
        nombre_receptions = receptions.count()
        montant_ht = nombre_receptions * 1200.00

        # Créer la facture
        facture = Facture.objects.create(
            client=client,
            date_facture=datetime.date.today(),
            date_echeance=datetime.date.today() + datetime.timedelta(days=30),
            montant_ht=montant_ht,
            notes=f"Facture groupée générée pour {nombre_receptions} réceptions d'essais.",
        )

        # Lier les réceptions à la facture
        receptions.update(facture=facture)

        messages.success(request, _(f"La facture {facture.reference} a été générée avec succès pour {nombre_receptions} réceptions."))
        return redirect('finance:facture_list')


# ============================================================
# 4. Vues Encaissement
# ============================================================

class EncaissementListView(ModulePermissionMixin, ListView):
    model = Encaissement
    template_name = 'finance/encaissement_list.html'
    context_object_name = 'encaissements'
    module_name = 'finance'
    action_name = 'view'


class EncaissementCreateView(ModulePermissionMixin, CreateView):
    model = Encaissement
    form_class = EncaissementForm
    template_name = 'finance/encaissement_form.html'
    success_url = reverse_lazy('finance:encaissement_list')
    module_name = 'finance'
    action_name = 'add'

    def get_initial(self):
        initial = super().get_initial()
        facture_id = self.request.GET.get('facture')
        if facture_id:
            facture = get_object_or_404(Facture, id=facture_id)
            initial['facture'] = facture
            initial['montant'] = facture.solde
        return initial

    def form_valid(self, form):
        messages.success(self.request, _("L'encaissement a été enregistré avec succès."))
        return super().form_valid(form)


# ============================================================
# 5. Vues Caisse & Trésorerie
# ============================================================

class CaisseListView(ModulePermissionMixin, ListView):
    model = MouvementCaisse
    template_name = 'finance/caisse_list.html'
    context_object_name = 'mouvements'
    module_name = 'finance'
    action_name = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calcul du solde actuel de la caisse
        entrees = MouvementCaisse.objects.filter(type_mouvement='ENTREE').aggregate(Sum('montant'))['montant__sum'] or 0
        sorties = MouvementCaisse.objects.filter(type_mouvement='SORTIE').aggregate(Sum('montant'))['montant__sum'] or 0
        context['solde_caisse'] = entrees - sorties
        return context


class MouvementCaisseCreateView(ModulePermissionMixin, CreateView):
    model = MouvementCaisse
    form_class = MouvementCaisseForm
    template_name = 'finance/mouvementcaisse_form.html'
    success_url = reverse_lazy('finance:caisse_list')
    module_name = 'finance'
    action_name = 'add'

    def form_valid(self, form):
        messages.success(self.request, _("Le mouvement de caisse a été enregistré."))
        return super().form_valid(form)


# ============================================================
# 6. Vues Suivi Recouvrement
# ============================================================

class RecouvrementListView(ModulePermissionMixin, ListView):
    model = Recouvrement
    template_name = 'finance/recouvrement_list.html'
    context_object_name = 'recouvrements'
    module_name = 'finance'
    action_name = 'view'

    def get_queryset(self):
        # Lister uniquement les dossiers de recouvrement non résolus
        return Recouvrement.objects.exclude(statut_recouvrement='RESOLU')


class RecouvrementUpdateView(ModulePermissionMixin, UpdateView):
    model = Recouvrement
    form_class = RecouvrementForm
    template_name = 'finance/recouvrement_form.html'
    success_url = reverse_lazy('finance:recouvrement_list')
    module_name = 'finance'
    action_name = 'change'

    def form_valid(self, form):
        # Mettre à jour automatiquement le nombre de rappels si un nouveau rappel a été effectué
        if form.has_changed() and 'dernier_rappel' in form.changed_data:
            form.instance.nombre_rappels += 1
        messages.success(self.request, _("Le dossier de recouvrement a été mis à jour."))
        return super().form_valid(form)


# ============================================================
# 7. Vues Facture Fournisseur (Dépenses)
# ============================================================

class FactureFournisseurListView(ModulePermissionMixin, ListView):
    model = FactureFournisseur
    template_name = 'finance/facturefournisseur_list.html'
    context_object_name = 'factures'
    module_name = 'finance'
    action_name = 'view'


class FactureFournisseurCreateView(ModulePermissionMixin, CreateView):
    model = FactureFournisseur
    form_class = FactureFournisseurForm
    template_name = 'finance/facturefournisseur_form.html'
    success_url = reverse_lazy('finance:facture_fournisseur_list')
    module_name = 'finance'
    action_name = 'add'

    def form_valid(self, form):
        messages.success(self.request, _("La facture fournisseur a été enregistrée."))
        return super().form_valid(form)


class PaiementCreateView(ModulePermissionMixin, CreateView):
    model = Paiement
    form_class = PaiementForm
    template_name = 'finance/paiement_form.html'
    success_url = reverse_lazy('finance:facture_fournisseur_list')
    module_name = 'finance'
    action_name = 'add'

    def get_initial(self):
        initial = super().get_initial()
        ff_id = self.request.GET.get('facture_fournisseur')
        if ff_id:
            ff = get_object_or_404(FactureFournisseur, id=ff_id)
            initial['facture_fournisseur'] = ff
            initial['montant'] = ff.solde
        return initial

    def form_valid(self, form):
        messages.success(self.request, _("Le paiement de la facture fournisseur a été enregistré."))
        return super().form_valid(form)


# ============================================================
# 8. Tableau de Bord Comptabilité & Rapports (P&L)
# ============================================================

class FinanceDashboardView(ModulePermissionMixin, TemplateView):
    template_name = 'finance/dashboard.html'
    module_name = 'finance'
    action_name = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Chiffre d'affaires global (Factures Validées/Payées)
        context['ca_total'] = Facture.objects.filter(
            statut__in=[Facture.StatutFacture.VALIDEE, Facture.StatutFacture.PAYEE_PARTIEL, Facture.StatutFacture.PAYEE]
        ).aggregate(Sum('montant_ttc'))['montant_ttc__sum'] or 0

        # Total des encaissements reçus
        context['total_encaissements'] = Encaissement.objects.filter(encaisse=True).aggregate(Sum('montant'))['montant__sum'] or 0

        # Total des dépenses fournisseurs payées
        context['total_depenses'] = Paiement.objects.aggregate(Sum('montant'))['montant__sum'] or 0

        # Reste à recouvrer (Solde des factures clients validées/partielles)
        factures_non_soldees = Facture.objects.filter(
            statut__in=[Facture.StatutFacture.VALIDEE, Facture.StatutFacture.PAYEE_PARTIEL]
        )
        total_du = factures_non_soldees.aggregate(Sum('montant_ttc'))['montant_ttc__sum'] or 0
        total_deja_paye = Encaissement.objects.filter(facture__in=factures_non_soldees, encaisse=True).aggregate(Sum('montant'))['montant__sum'] or 0
        context['reste_a_recouvrer'] = total_du - total_deja_paye

        # Balance de trésorerie (Entrées - Sorties de caisse)
        entrees = MouvementCaisse.objects.filter(type_mouvement='ENTREE').aggregate(Sum('montant'))['montant__sum'] or 0
        sorties = MouvementCaisse.objects.filter(type_mouvement='SORTIE').aggregate(Sum('montant'))['montant__sum'] or 0
        context['solde_caisse'] = entrees - sorties

        # Liste des 5 dernières factures clients
        context['recent_factures'] = Facture.objects.order_by('-date_facture')[:5]

        # Liste des 5 derniers mouvements de caisse
        context['recent_mouvements'] = MouvementCaisse.objects.order_by('-date_mouvement')[:5]

        return context


# ============================================================
# 9. Exports de journaux comptables (CSV)
# ============================================================

class ExportVentesCSVView(ModulePermissionMixin, View):
    module_name = 'finance'
    action_name = 'view'

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="journal_ventes.csv"'
        response.write('\ufeff'.encode('utf8')) # BOM pour Excel

        writer = csv.writer(response, delimiter=';')
        writer.writerow(['N° Facture', 'Date', 'Client', 'Montant HT', 'TVA', 'Montant TTC', 'Statut'])

        factures = Facture.objects.all().order_by('date_facture')
        for f in factures:
            writer.writerow([
                f.reference,
                f.date_facture.strftime('%d/%m/%Y'),
                f.client.nom,
                f.montant_ht,
                f.montant_tva,
                f.montant_ttc,
                f.get_statut_display()
            ])
        return response


class ExportAchatsCSVView(ModulePermissionMixin, View):
    module_name = 'finance'
    action_name = 'view'

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="journal_achats.csv"'
        response.write('\ufeff'.encode('utf8')) # BOM pour Excel

        writer = csv.writer(response, delimiter=';')
        writer.writerow(['Réf Interne', 'N° Facture Fournisseur', 'Date', 'Fournisseur', 'Montant HT', 'TVA', 'Montant TTC', 'Statut'])

        factures = FactureFournisseur.objects.all().order_by('date_facture')
        for f in factures:
            writer.writerow([
                f.reference_interne,
                f.reference_fournisseur,
                f.date_facture.strftime('%d/%m/%Y'),
                f.fournisseur.nom,
                f.montant_ht,
                f.montant_tva,
                f.montant_ttc,
                f.get_statut_display()
            ])
        return response


# ============================================================
# 10. AJAX Views for Invoicing Lines (Image 2 Features)
# ============================================================

class LoadDevisLinesView(ModulePermissionMixin, View):
    module_name = 'finance'
    action_name = 'view'

    def get(self, request, *args, **kwargs):
        devis_id = request.GET.get('devis_id')
        devis = get_object_or_404(Devis, id=devis_id)
        lines = []
        for detail in devis.details.all():
            lines.append({
                'num_prix': detail.num_prix,
                'designation': detail.designation,
                'unite': detail.unite,
                'quantite': float(detail.quantite),
                'prix_unitaire': float(detail.prix_unitaire),
                'prix_total': float(detail.prix_total)
            })
        return JsonResponse({'lines': lines})


class LoadInvoiceLinesView(ModulePermissionMixin, View):
    module_name = 'finance'
    action_name = 'view'

    def get(self, request, *args, **kwargs):
        facture_id = request.GET.get('facture_id')
        facture = get_object_or_404(Facture, id=facture_id)
        lines = []
        for line in facture.lignes.all():
            lines.append({
                'num_prix': line.num_prix,
                'designation': line.designation,
                'unite': line.unite,
                'quantite': float(line.quantite),
                'prix_unitaire': float(line.prix_unitaire),
                'prix_total': float(line.prix_total)
            })
        return JsonResponse({'lines': lines})


class SaveInvoiceLineView(ModulePermissionMixin, View):
    module_name = 'finance'
    action_name = 'change'

    def post(self, request, *args, **kwargs):
        facture_id = request.POST.get('facture_id')
        facture = get_object_or_404(Facture, id=facture_id)
        line_id = request.POST.get('line_id')
        
        num_prix = request.POST.get('num_prix', '')
        designation = request.POST.get('designation', '')
        unite = request.POST.get('unite', '')
        quantite = request.POST.get('quantite', '1')
        prix_unitaire = request.POST.get('prix_unitaire', '0')
        
        if line_id:
            line = get_object_or_404(LigneFacture, id=line_id, facture=facture)
            line.num_prix = num_prix
            line.designation = designation
            line.unite = unite
            line.quantite = quantite
            line.prix_unitaire = prix_unitaire
            line.save()
        else:
            line = LigneFacture.objects.create(
                facture=facture,
                num_prix=num_prix,
                designation=designation,
                unite=unite,
                quantite=quantite,
                prix_unitaire=prix_unitaire
            )
        
        facture.recalculate_totals()
        
        # Render a simple dictionary of all lines to send back
        lignes_list = []
        for l in facture.lignes.all():
            lignes_list.append({
                'id': l.id,
                'num_prix': l.num_prix,
                'designation': l.designation,
                'unite': l.unite,
                'quantite': float(l.quantite),
                'prix_unitaire': float(l.prix_unitaire),
                'prix_total': float(l.prix_total)
            })
            
        return JsonResponse({
            'status': 'success',
            'lines': lignes_list,
            'total_ht': float(facture.montant_ht),
            'total_tva': float(facture.montant_tva),
            'total_ttc': float(facture.montant_ttc)
        })


class DeleteInvoiceLineView(ModulePermissionMixin, View):
    module_name = 'finance'
    action_name = 'change'

    def post(self, request, *args, **kwargs):
        line_id = request.POST.get('line_id')
        line = get_object_or_404(LigneFacture, id=line_id)
        facture = line.facture
        line.delete()
        
        # Recalculate totals
        facture.recalculate_totals()
        
        lignes_list = []
        for l in facture.lignes.all():
            lignes_list.append({
                'id': l.id,
                'num_prix': l.num_prix,
                'designation': l.designation,
                'unite': l.unite,
                'quantite': float(l.quantite),
                'prix_unitaire': float(l.prix_unitaire),
                'prix_total': float(l.prix_total)
            })
            
        return JsonResponse({
            'status': 'success',
            'lines': lignes_list,
            'total_ht': float(facture.montant_ht),
            'total_tva': float(facture.montant_tva),
            'total_ttc': float(facture.montant_ttc)
        })


class ImportLinesBulkView(ModulePermissionMixin, View):
    module_name = 'finance'
    action_name = 'change'

    def post(self, request, *args, **kwargs):
        facture_id = request.POST.get('facture_id')
        source_type = request.POST.get('source_type')
        source_id = request.POST.get('source_id')
        facture = get_object_or_404(Facture, id=facture_id)
        
        # Clear existing lines to prevent duplicates
        facture.lignes.all().delete()
        
        if source_type == 'devis':
            devis = get_object_or_404(Devis, id=source_id)
            for d in devis.details.all():
                LigneFacture.objects.create(
                    facture=facture,
                    num_prix=d.num_prix,
                    designation=d.designation,
                    unite=d.unite,
                    quantite=d.quantite,
                    prix_unitaire=d.prix_unitaire
                )
        elif source_type == 'facture':
            src_facture = get_object_or_404(Facture, id=source_id)
            for l in src_facture.lignes.all():
                LigneFacture.objects.create(
                    facture=facture,
                    num_prix=l.num_prix,
                    designation=l.designation,
                    unite=l.unite,
                    quantite=l.quantite,
                    prix_unitaire=l.prix_unitaire
                )
                
        facture.recalculate_totals()
        
        lignes_list = []
        for l in facture.lignes.all():
            lignes_list.append({
                'id': l.id,
                'num_prix': l.num_prix,
                'designation': l.designation,
                'unite': l.unite,
                'quantite': float(l.quantite),
                'prix_unitaire': float(l.prix_unitaire),
                'prix_total': float(l.prix_total)
            })
            
        return JsonResponse({
            'status': 'success',
            'lines': lignes_list,
            'total_ht': float(facture.montant_ht),
            'total_tva': float(facture.montant_tva),
            'total_ttc': float(facture.montant_ttc)
        })
