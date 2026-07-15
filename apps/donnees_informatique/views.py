from django.views.generic import TemplateView
from apps.core.mixins import ModulePermissionMixin

class PlaceholderDashboardView(ModulePermissionMixin, TemplateView):
    template_name = 'placeholder_dashboard.html'
    module_name = 'commercial'
    action_name = 'view'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Données Informatique"
        return context
