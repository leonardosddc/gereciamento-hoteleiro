from django.urls import path
from .views.home import dashboard
from .views.hospede import cadastrar_hospede, listar_hospedes, editar_hospede, excluir_hospede
from .views.quarto import cadastrar_quarto, listar_quartos, editar_quarto, excluir_quarto
from .views.reserva import cadastrar_reserva, listar_reservas, editar_reserva, excluir_reserva # NOVA IMPORTAÇÃO

urlpatterns = [
    path('', dashboard, name='dashboard'),

    # Hóspedes
    path('hospedes/', listar_hospedes, name='listar_hospedes'),
    path('hospedes/novo/', cadastrar_hospede, name='cadastrar_hospede'),
    path('hospedes/editar/<int:id>/', editar_hospede, name='editar_hospede'),
    path('hospedes/excluir/<int:id>/', excluir_hospede, name='excluir_hospede'),
    
    # Quartos
    path('quartos/', listar_quartos, name='listar_quartos'),
    path('quartos/novo/', cadastrar_quarto, name='cadastrar_quarto'),
    path('quartos/editar/<int:id>/', editar_quarto, name='editar_quarto'),
    path('quartos/excluir/<int:id>/', excluir_quarto, name='excluir_quarto'),

    # Reservas (NOVAS ROTAS)
    path('reservas/', listar_reservas, name='listar_reservas'),
    path('reservas/novo/', cadastrar_reserva, name='cadastrar_reserva'),
    path('reservas/editar/<int:id>/', editar_reserva, name='editar_reserva'),
    path('reservas/excluir/<int:id>/', excluir_reserva, name='excluir_reserva'),
]