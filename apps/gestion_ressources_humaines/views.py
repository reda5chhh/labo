from django.views.generic import TemplateView
from apps.core.mixins import ModulePermissionMixin

class PlaceholderDashboardView(ModulePermissionMixin, TemplateView):
    template_name = 'placeholder_dashboard.html'
    action_name = 'view'
    
    @property
    def module_name(self):
        tab = self.request.GET.get('tab')
        if tab == 'conges':
            return 'conges_rh'
        elif tab == 'attestations':
            return 'attestations_rh'
        
        valid_tabs = ['personnel', 'stagiaires', 'paie', 'qualification']
        if tab in valid_tabs:
            return tab
        return 'personnel' # default fallback
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tab = self.request.GET.get('tab')
        titles = {
            'personnel': "Table Personnel",
            'conges': "Table des Congés (RH)",
            'attestations': "Table des Attestations (RH)",
            'stagiaires': "Table des Stagiaires",
            'paie': "Table de Paie",
            'qualification': "Table de Qualification",
        }
        context['title'] = titles.get(tab, "Table Personnel")
        return context

