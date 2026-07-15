from django.urls import path
from . import views

app_name = 'specimen_signature'

urlpatterns = [
    path('', views.PlaceholderDashboardView.as_view(), name='dashboard'),
]
