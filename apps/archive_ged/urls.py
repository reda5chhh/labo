from django.urls import path
from . import views

app_name = 'archive_ged'

urlpatterns = [
    path('', views.PlaceholderDashboardView.as_view(), name='dashboard'),
]
