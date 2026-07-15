from django.urls import path
from . import views

app_name = 'suivi_modifications'

urlpatterns = [
    path('', views.AuditLogListView.as_view(), name='dashboard'),
]
