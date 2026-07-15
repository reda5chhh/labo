from django.urls import path
from . import views

app_name = 'marches'

urlpatterns = [
    # Appels d'offres, Cautions, Décomptes (Vue regroupée en onglets)
    path('appels-offres/', views.AOListView.as_view(), name='ao_list'),

    # AOSoumission
    path('appels-offres/soumissions/creer/', views.AOSoumissionCreateView.as_view(), name='aosoumission_create'),
    path('appels-offres/soumissions/<int:pk>/modifier/', views.AOSoumissionUpdateView.as_view(), name='aosoumission_update'),
    path('appels-offres/soumissions/<int:pk>/annuler/', views.AOSoumissionAnnulerView.as_view(), name='aosoumission_delete'),
    path('appels-offres/soumissions/<int:pk>/restaurer/', views.AOSoumissionRestaurerView.as_view(), name='aosoumission_restore'),

    # AOAdjuge
    path('appels-offres/adjudications/creer/', views.AOAdjugeCreateView.as_view(), name='aoadjuge_create'),
    path('appels-offres/adjudications/<int:pk>/modifier/', views.AOAdjugeUpdateView.as_view(), name='aoadjuge_update'),
    path('appels-offres/adjudications/<int:pk>/annuler/', views.AOAdjugeAnnulerView.as_view(), name='aoadjuge_delete'),
    path('appels-offres/adjudications/<int:pk>/restaurer/', views.AOAdjugeRestaurerView.as_view(), name='aoadjuge_restore'),

    # Cautions
    path('cautions/creer/', views.CautionCreateView.as_view(), name='caution_create'),
    path('cautions/<int:pk>/modifier/', views.CautionUpdateView.as_view(), name='caution_update'),
    path('cautions/<int:pk>/annuler/', views.CautionAnnulerView.as_view(), name='caution_delete'),
    path('cautions/<int:pk>/restaurer/', views.CautionRestaurerView.as_view(), name='caution_restore'),

    # Décomptes
    path('decomptes/creer/', views.DecompteCreateView.as_view(), name='decompte_create'),
    path('decomptes/<int:pk>/modifier/', views.DecompteUpdateView.as_view(), name='decompte_update'),
    path('decomptes/<int:pk>/annuler/', views.DecompteAnnulerView.as_view(), name='decompte_delete'),
    path('decomptes/<int:pk>/restaurer/', views.DecompteRestaurerView.as_view(), name='decompte_restore'),

    # Résultats / Enquêtes satisfaction
    path('resultats-bc/', views.ResultatBCListView.as_view(), name='resultatbc_list'),
    path('resultats-bc/valider/', views.ResultatBCValiderView.as_view(), name='resultatbc_valider'),
    path('ajax/load-decompte-details/', views.DecompteDetailAjaxView.as_view(), name='ajax_load_decompte_details'),
]
