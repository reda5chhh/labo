from django.views.generic import TemplateView
from apps.core.mixins import ModulePermissionMixin

class PlaceholderDashboardView(ModulePermissionMixin, TemplateView):
    template_name = 'placeholder_dashboard.html'
    action_name = 'view'
    
    @property
    def module_name(self):
        tab = self.request.GET.get('tab')
        if tab in ['fiche_qualification', 'feuilles_qualification']:
            return tab
        return 'fiche_qualification' # default fallback
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tab = self.request.GET.get('tab')
        if tab == 'feuilles_qualification':
            context['title'] = "Feuilles de Qualification"
        else:
            context['title'] = "Fiche de qualification"
        return context

