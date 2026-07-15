from django.urls import path
from . import views

app_name = 'droits_ged'

urlpatterns = [
    path('', views.PlaceholderDashboardView.as_view(), name='dashboard'),
]
