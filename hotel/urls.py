from django.urls import path
from .views.home import dashboard
from .views.hospede import cadastrar_hospede, listar_hospedes, editar_hospede, excluir_hospede
from .views.quarto import cadastrar_quarto, listar_quartos, editar_quarto, excluir_quarto

urlpatterns = [
    # Menu Principal
    path('', dashboard, name='dashboard'),

    # Rotas de Hóspedes
    path('hospedes/', listar_hospedes, name='listar_hospedes'),
    path('hospedes/novo/', cadastrar_hospede, name='cadastrar_hospede'),
    path('hospedes/editar/<int:id>/', editar_hospede, name='editar_hospede'),
    path('hospedes/excluir/<int:id>/', excluir_hospede, name='excluir_hospede'),
    
    # Rotas de Quartos
    path('quartos/', listar_quartos, name='listar_quartos'),
    path('quartos/novo/', cadastrar_quarto, name='cadastrar_quarto'),
    path('quartos/editar/<int:id>/', editar_quarto, name='editar_quarto'),
    path('quartos/excluir/<int:id>/', excluir_quarto, name='excluir_quarto'),
]