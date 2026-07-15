from django.views.generic import TemplateView
from apps.core.mixins import ModulePermissionMixin

class PlaceholderDashboardView(ModulePermissionMixin, TemplateView):
    template_name = 'placeholder_dashboard.html'
    action_name = 'view'
    
    @property
    def module_name(self):
        tab = self.request.GET.get('tab')
        valid_tabs = [
            'donnees_balances', 'masses_etalons', 'donnees_materiel', 
            'periodicite', 'instruction_etalonnage', 'type_intervention', 'accreditation'
        ]
        if tab in valid_tabs:
            return tab
        return 'donnees_balances' # default fallback
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tab = self.request.GET.get('tab')
        titles = {
            'donnees_balances': "Données Balances",
            'masses_etalons': "Données Masses Étalons",
            'donnees_materiel': "Données Matériel",
            'periodicite': "Périodicité",
            'instruction_etalonnage': "Instruction Étalonnage",
            'type_intervention': "Type Intervention",
            'accreditation': "Accréditation"
        }
        context['title'] = titles.get(tab, "Données Balances")
        return context

