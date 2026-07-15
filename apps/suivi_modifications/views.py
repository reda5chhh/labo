from django.views.generic import ListView
from django.db.models import Q
from apps.core.mixins import ModulePermissionMixin
from apps.core.models import AuditLog, User

class AuditLogListView(ModulePermissionMixin, ListView):
    model = AuditLog
    template_name = 'suivi_modifications/log_list.html'
    module_name = 'suivi_modifications'
    action_name = 'view'
    context_object_name = 'logs'
    paginate_by = 50

    def get_queryset(self):
        # We start with get_queryset from super() which secures permissions
        # and returns qs.none() if they have no view permission
        qs = super().get_queryset()
        
        # Get query parameters
        action_type = self.request.GET.get('action_type')
        user_id = self.request.GET.get('user_id')
        model_name = self.request.GET.get('model_name')
        date_du = self.request.GET.get('date_du')
        date_au = self.request.GET.get('date_au')
        search = self.request.GET.get('search')

        if action_type:
            qs = qs.filter(action_type=action_type)
        if user_id:
            try:
                qs = qs.filter(user_id=int(user_id))
            except ValueError:
                pass
        if model_name:
            qs = qs.filter(model_name=model_name)
        if date_du:
            qs = qs.filter(timestamp__date__gte=date_du)
        if date_au:
            qs = qs.filter(timestamp__date__lte=date_au)
        if search:
            qs = qs.filter(
                Q(object_repr__icontains=search) |
                Q(ip_address__icontains=search) |
                Q(user_agent__icontains=search) |
                Q(model_name__icontains=search)
            )
        
        return qs.select_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Serialize only the paginated log records
        import json
        from django.core.serializers.json import DjangoJSONEncoder
        for log in context['object_list']:
            log.old_value_json = json.dumps(log.old_value, cls=DjangoJSONEncoder) if log.old_value else '{}'
            log.new_value_json = json.dumps(log.new_value, cls=DjangoJSONEncoder) if log.new_value else '{}'

        # Fetch filter metadata
        context['users'] = User.objects.all().order_by('last_name', 'first_name')
        context['action_choices'] = AuditLog.ActionType.choices
        
        # Dynamically fetch unique model names present in audit log
        context['models_logged'] = AuditLog.objects.exclude(model_name='').values_list('model_name', flat=True).distinct().order_by('model_name')
        
        # Retain active filter inputs
        context['active_action_type'] = self.request.GET.get('action_type', '')
        context['active_user_id'] = self.request.GET.get('user_id', '')
        context['active_model_name'] = self.request.GET.get('model_name', '')
        context['active_date_du'] = self.request.GET.get('date_du', '')
        context['active_date_au'] = self.request.GET.get('date_au', '')
        context['active_search'] = self.request.GET.get('search', '')
        
        context['title'] = "Suivi des modifications"
        return context
