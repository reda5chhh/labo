from django.views.generic import TemplateView
from apps.core.mixins import ModulePermissionMixin

class PlaceholderDashboardView(ModulePermissionMixin, TemplateView):
    template_name = 'placeholder_dashboard.html'
    action_name = 'view'
    
    @property
    def module_name(self):
        tab = self.request.GET.get('tab')
        valid_tabs = [
            'suivi_docs', 'liste_suivi', 'revue_doc', 'veille_normative', 'controle_enreg', 'abbreviations'
        ]
        if tab in valid_tabs:
            return tab
        return 'suivi_docs' # default fallback
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tab = self.request.GET.get('tab')
        titles = {
            'suivi_docs': "Suivi documents",
            'liste_suivi': "Liste suivi docs",
            'revue_doc': "Revue documentaire",
            'veille_normative': "Veille Normative",
            'controle_enreg': "Contrôle enregistrements",
            'abbreviations': "Abréviations",
        }
        context['title'] = titles.get(tab, "Suivi documents")
        return context

