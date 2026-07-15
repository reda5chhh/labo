from django.views.generic import TemplateView
from apps.core.mixins import ModulePermissionMixin

class PlaceholderDashboardView(ModulePermissionMixin, TemplateView):
    template_name = 'placeholder_dashboard.html'
    action_name = 'view'
    
    @property
    def module_name(self):
        tab = self.request.GET.get('tab')
        if tab == 'planning_maintenance':
            return 'planning_maintenance_labo'
        
        valid_tabs = [
            'preparation_bleu', 'solution_lavante', 'suivi_balances', 'temperature_bassins',
            'fiche_maintenance', 'gestion_consommable', 'conditions_ambiantes', 'controle_eau'
        ]
        if tab in valid_tabs:
            return tab
        return 'preparation_bleu' # default fallback
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tab = self.request.GET.get('tab')
        titles = {
            'preparation_bleu': "Préparation bleu",
            'solution_lavante': "Solution lavante",
            'suivi_balances': "Suivi des balances",
            'temperature_bassins': "Température Bassins",
            'planning_maintenance': "Planning maintenance (Labo)",
            'fiche_maintenance': "Fiche maintenance",
            'gestion_consommable': "Gestion consommable",
            'conditions_ambiantes': "Conditions ambiantes",
            'controle_eau': "Contrôle eau distillée",
        }
        context['title'] = titles.get(tab, "Préparation bleu")
        return context

