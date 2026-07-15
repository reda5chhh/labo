from django.urls import path
from . import views

app_name = 'services_familles_ged'

urlpatterns = [
    path('', views.PlaceholderDashboardView.as_view(), name='dashboard'),
]
