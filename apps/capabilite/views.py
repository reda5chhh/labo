from django.views.generic import TemplateView
from apps.core.mixins import ModulePermissionMixin

class PlaceholderDashboardView(ModulePermissionMixin, TemplateView):
    template_name = 'placeholder_dashboard.html'
    action_name = 'view'
    
    @property
    def module_name(self):
        tab = self.request.GET.get('tab')
        if tab in ['moyens_mesure', 'balances']:
            return tab
        return 'moyens_mesure' # default fallback
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tab = self.request.GET.get('tab')
        if tab == 'balances':
            context['title'] = "Capabilité des Balances"
        else:
            context['title'] = "Capabilité des Moyens de Mesure"
        return context

