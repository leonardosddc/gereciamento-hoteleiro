from django.shortcuts import render, redirect, get_object_or_404
from ..models.reserva import Reserva
from ..models.consumacao import Consumacao
from ..forms.consumacao import ConsumacaoForm

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

def liquidar_consumacao(request, consumacao_id):
    """
    Botão rápido para dar baixa (mudar pago para True) - RF10
    """
    consumacao = get_object_or_404(Consumacao, id=consumacao_id)
    consumacao.pago = True
    consumacao.save()
    # Volta para a tela de gerenciamento daquela mesma reserva
    return redirect('gerenciar_consumacao', reserva_id=consumacao.reserva.id)
