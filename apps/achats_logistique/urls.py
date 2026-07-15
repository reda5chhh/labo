from django.urls import path
from . import views

app_name = 'achats_logistique'

urlpatterns = [
    path('', views.PlaceholderDashboardView.as_view(), name='dashboard'),
]
