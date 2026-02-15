# workflow/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # Page visible par le citoyen
    path('suivi/<uuid:uuid>/', views.suivi_public, name='suivi_public'),
    
    # API consommée par le Javascript (D3.js)
    path('api/graph/<uuid:uuid>/', views.graph_data, name='graph_data'),
]
