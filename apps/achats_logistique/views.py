from django.views.generic import TemplateView
from apps.core.mixins import ModulePermissionMixin

class PlaceholderDashboardView(ModulePermissionMixin, TemplateView):
    template_name = 'placeholder_dashboard.html'
    action_name = 'view'
    
    @property
    def module_name(self):
        tab = self.request.GET.get('tab')
        valid_tabs = [
            'bci', 'demande_prix', 'prestataires_externes', 'bons_commandes',
            'bons_reception', 'evaluation_prestataires', 'prestataires_agrees', 'cahier_charges'
        ]
        if tab in valid_tabs:
            return tab
        return 'bci' # default fallback
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tab = self.request.GET.get('tab')
        titles = {
            'bci': "Bons de Commande Internes",
            'demande_prix': "Demande de Prix",
            'prestataires_externes': "Sélection Prestataires Externes",
            'bons_commandes': "Bons de Commande",
            'bons_reception': "Bons de Réception",
            'evaluation_prestataires': "Évaluation Prestataires",
            'prestataires_agrees': "Prestataires Agréés",
            'cahier_charges': "Cahiers des Charges",
        }
        context['title'] = titles.get(tab, "Achats et logistique")
        return context

