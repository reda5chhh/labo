from django.urls import path
from . import views

app_name = 'formation_qualification'

urlpatterns = [
    path('', views.PlaceholderDashboardView.as_view(), name='dashboard'),
]
