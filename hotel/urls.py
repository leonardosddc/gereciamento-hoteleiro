from django.urls import path
from .views.home import dashboard
from .views.hospede import cadastrar_hospede, listar_hospedes, editar_hospede, excluir_hospede
from .views.quarto import cadastrar_quarto, listar_quartos, editar_quarto, excluir_quarto
from .views.reserva import cadastrar_reserva, listar_reservas, editar_reserva, excluir_reserva
from .views.pagamento import (
    cadastrar_pagamento,
    listar_pagamentos,
    editar_pagamento,
    excluir_pagamento,
    gerar_link_pagamento,
    webhook_mercado_pago
)
from .views.consumacao import gerenciar_consumacao, liquidar_consumacao

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

    # Pagamentos (NOVAS ROTAS)
    path('pagamentos/', listar_pagamentos, name='listar_pagamentos'),
    path('pagamentos/novo/', cadastrar_pagamento, name='cadastrar_pagamento'),
    path('pagamentos/editar/<int:id>/', editar_pagamento, name='editar_pagamento'),
    path('pagamentos/excluir/<int:id>/', excluir_pagamento, name='excluir_pagamento'),


    # NOVAS ROTAS DA INTEGRAÇÃO
    # Rota para o botão de "Gerar PIX"
    path('pagamentos/gerar-link/<int:pagamento_id>/', gerar_link_pagamento, name='gerar_link_pagamento'),
    
    # Rota do Webhook (A URL que você vai cadastrar lá no painel do Mercado Pago)
    path('webhook/mercadopago/', webhook_mercado_pago, name='webhook_mp'),

    # Consumação (NOVAS ROTAS)
    path('reservas/<int:reserva_id>/consumacao/', gerenciar_consumacao, name='gerenciar_consumacao'),
    path('consumacao/liquidar/<int:consumacao_id>/', liquidar_consumacao, name='liquidar_consumacao'),
]