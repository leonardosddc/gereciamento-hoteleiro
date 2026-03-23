from django.urls import path
from .views.hospede import cadastrar_hospede # Use o ponto (.) para importação relativa

urlpatterns = [
    path('hospedes/novo/', cadastrar_hospede, name='cadastrar_hospede'),
]