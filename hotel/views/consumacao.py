import os
import mercadopago
from django.contrib.auth.decorators import login_required # 1. Importe o decorador
from django.shortcuts import render, redirect, get_object_or_404
from ..models.reserva import Reserva
from ..models.consumacao import Consumacao
from ..models.pagamento import Pagamento
from ..forms.consumacao import ConsumacaoForm

@login_required
def gerenciar_consumacao(request, reserva_id):
    """
    Tela exclusiva da reserva (RF09) que lista o que o hóspede consumiu
    e permite adicionar novos itens.
    """
    reserva = get_object_or_404(Reserva, id=reserva_id)
    consumacoes = reserva.consumacoes.all().order_by('-data_lancamento')
    
    # Calcula o total que falta pagar
    total_pendente = sum(c.valor_total for c in consumacoes if not c.pago)

    if request.method == 'POST':
        form = ConsumacaoForm(request.POST)
        if form.is_valid():
            nova_consumacao = form.save(commit=False)
            nova_consumacao.reserva = reserva # Vincula a consumação a esta reserva
            nova_consumacao.save()
            return redirect('gerenciar_consumacao', reserva_id=reserva.id)
    else:
        form = ConsumacaoForm()

    contexto = {
        'reserva': reserva,
        'consumacoes': consumacoes,
        'form': form,
        'total_pendente': total_pendente
    }
    return render(request, 'consumacao/gerenciar_consumacao.html', contexto)

@login_required
def liquidar_consumacao(request, consumacao_id):
    """
    Botão rápido para dar baixa (mudar pago para True) - RF10
    """
    consumacao = get_object_or_404(Consumacao, id=consumacao_id)
    consumacao.pago = True
    consumacao.save()
    # Volta para a tela de gerenciamento daquela mesma reserva
    return redirect('gerenciar_consumacao', reserva_id=consumacao.reserva.id)

@login_required
def pagar_consumacao_online(request, reserva_id):
    """ Gera um link de checkout do Mercado Pago para TODAS as consumações pendentes daquela reserva """
    reserva = get_object_or_404(Reserva, id=reserva_id)
    consumacoes_pendentes = reserva.consumacoes.filter(pago=False)
    
    total_pendente = sum(c.valor_total for c in consumacoes_pendentes)
    
    if total_pendente <= 0:
        return redirect('gerenciar_consumacao', reserva_id=reserva.id)
        
    # 1. Cria um registro em Pagamento histórico (Marcamos como tipo diferente se quiser, mas usaremos Pix/Cartão padrão)
    pagamento = Pagamento.objects.create(
        reserva=reserva,
        valor_total=total_pendente,
        status='PENDENTE'
    )
    
    # 2. Configura o SDK do Mercado Pago
    sdk = mercadopago.SDK(os.getenv("MERCADO_PAGO_ACCESS_TOKEN"))
    
    # 3. Monta os dados (adicionando uma tag especial no título para o webhook saber diferenciar)
    preference_data = {
        "items": [
            {
                "id": f"CONSUMACAO_{pagamento.id}", # ID especial com prefixo
                "title": f"Consumações Pendentes - Reserva {reserva.id}",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": float(total_pendente),
            }
        ],
        "payer": {
            "name": reserva.hospede.nome,
            "email": reserva.hospede.email,
        },
        "external_reference": f"CONSUMACAO_{pagamento.id}", # Tag crucial para o Webhook identificar
        "notification_url": f"{os.getenv("DOMINIO_SISTEMA")}/webhook/mercadopago/",
    }
    
    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]
    
    if preference.get("id"):
        pagamento.id_transacao_externa = preference.get("id")
        pagamento.link_pagamento = preference.get("sandbox_init_point")
        pagamento.save()
        
        # Redireciona o hóspede direto para a tela de pagamento do Mercado Pago
        return redirect(pagamento.link_pagamento)
        
    return redirect('gerenciar_consumacao', reserva_id=reserva.id)