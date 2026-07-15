from django.urls import path
from . import views

app_name = 'parametrage_general'

urlpatterns = [
    path('', views.PlaceholderDashboardView.as_view(), name='dashboard'),
]
