# dossiers/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('nouveau/', views.plainte_create, name='plainte_create'),
    path('dossier/<uuid:uuid>/', views.plainte_detail, name='plainte_detail'),
    path('dossier/<uuid:uuid>/recepisse/', views.generer_recepisse, name='recepisse_print'),
    path('dossier/<uuid:uuid>/add_piece/', views.ajouter_piece, name='ajouter_piece'),
]