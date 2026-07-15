from django.urls import path
from . import views

app_name = 'attestations'

urlpatterns = [
    path('', views.PlaceholderDashboardView.as_view(), name='dashboard'),
]
