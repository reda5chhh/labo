"""
LABO.COS App — Administration Django pour l'application core.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, AuditLog
from .forms import UserAdminCreationForm, UserAdminChangeForm


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Administration personnalisée du modèle User."""
    add_form = UserAdminCreationForm
    form = UserAdminChangeForm
    model = User

    list_display = [
        'username', 'get_full_name', 'email',
        'fonction', 'est_admin', 'is_active', 'date_joined'
    ]
    list_filter = ['est_admin', 'is_active', 'is_staff']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'fonction']

    fieldsets = UserAdmin.fieldsets + (
        (_('Informations LABO.COS'), {
            'fields': ('fonction', 'signature_image', 'est_admin'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (_('Informations LABO.COS'), {
            'fields': ('first_name', 'last_name', 'email', 'fonction', 'est_admin'),
        }),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Administration en lecture seule du journal d'audit."""
    list_display = [
        'timestamp', 'user', 'action_type',
        'model_name', 'object_id', 'ip_address'
    ]
    list_filter = ['action_type', 'model_name']
    search_fields = ['user__username', 'model_name', 'object_repr', 'ip_address']
    readonly_fields = [
        'user', 'action_type', 'model_name', 'object_id',
        'object_repr', 'old_value', 'new_value',
        'ip_address', 'user_agent', 'timestamp'
    ]
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']

    def has_add_permission(self, request):
        """Interdire l'ajout manuel d'entrées dans l'audit log."""
        return False

    def has_change_permission(self, request, obj=None):
        """Interdire la modification des entrées d'audit log."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Seuls les superusers peuvent supprimer les logs (archivage)."""
        return request.user.is_superuser


# Configuration globale de l'admin Django
admin.site.site_header = 'LABO.COS — Administration'
admin.site.site_title = 'LABO.COS Admin'
admin.site.index_title = 'Tableau de bord Administration'
