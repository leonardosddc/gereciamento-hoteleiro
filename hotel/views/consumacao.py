import os
import mercadopago
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from ..models.reserva import Reserva
from ..models.consumacao import Consumacao
from ..models.pagamento import Pagamento
from ..forms.consumacao import ConsumacaoForm

@login_required
def gerenciar_consumacao(request, reserva_id):
    """
    Tela exclusiva da reserva que lista o que o hóspede consumiu
    e permite adicionar novos itens.
    """
    reserva = get_object_or_404(Reserva, id=reserva_id)
    consumacoes = reserva.consumacoes.all().order_by('-data_lancamento')
    
    total_pendente = sum(c.valor_total for c in consumacoes if not c.pago)

    if request.method == 'POST':
        form = ConsumacaoForm(request.POST)
        if form.is_valid():
            nova_consumacao = form.save(commit=False)
            nova_consumacao.reserva = reserva
            nova_consumacao.save()
            
            # --- NOVA LÓGICA DE ESPELHAMENTO ---
            # Ao lançar a consumação, cria IMEDIATAMENTE um Pagamento correspondente a ela
            status_pagamento = 'CONCLUIDO' if nova_consumacao.pago else 'PENDENTE'
            metodo_pagamento = 'DINHEIRO' if nova_consumacao.pago else None
            data_pag = timezone.now() if nova_consumacao.pago else None
            
            Pagamento.objects.create(
                reserva=reserva,
                valor_total=nova_consumacao.valor_total,
                status=status_pagamento,
                metodo=metodo_pagamento,
                data_pagamento=data_pag,
                # Etiqueta secreta para sabermos qual pagamento pertence a qual consumação
                id_transacao_externa=f"ITEM_CONS_{nova_consumacao.id}" 
            )
            
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
    Botão rápido para dar baixa (mudar pago para True) e concluir o pagamento pendente.
    """
    consumacao = get_object_or_404(Consumacao, id=consumacao_id)
    
    if not consumacao.pago:
        # 1. Quita na consumação
        consumacao.pago = True
        consumacao.save()
        
        # 2. Busca O PAGAMENTO EXATO vinculado a esta consumação através da etiqueta
        pagamento_vinculado = Pagamento.objects.filter(
            reserva=consumacao.reserva,
            id_transacao_externa=f"ITEM_CONS_{consumacao.id}"
        ).first()
        
        # 3. Se ele achar o pendente, atualiza para Concluído. 
        if pagamento_vinculado:
            pagamento_vinculado.status = 'CONCLUIDO'
            pagamento_vinculado.metodo = 'DINHEIRO'
            pagamento_vinculado.data_pagamento = timezone.now()
            pagamento_vinculado.save()
        else:
            # Fallback de segurança caso alguém tenha apagado manualmente o pagamento
            Pagamento.objects.create(
                reserva=consumacao.reserva,
                valor_total=consumacao.valor_total,
                status='CONCLUIDO',
                metodo='DINHEIRO',
                data_pagamento=timezone.now(),
                id_transacao_externa=f"ITEM_CONS_{consumacao.id}"
            )
        
        # 4. Invalida links combo do Mercado Pago que possam estar ativos com valor antigo
        Pagamento.objects.filter(reserva=consumacao.reserva, status='PENDENTE').exclude(id_transacao_externa__startswith="ITEM_CONS_").delete()
        
    return redirect('gerenciar_consumacao', reserva_id=consumacao.reserva.id)


@login_required
def pagar_consumacao_online(request, reserva_id):
    """ 
    Gera um link de checkout do Mercado Pago e atrela a todos os itens pendentes
    """
    reserva = get_object_or_404(Reserva, id=reserva_id)
    consumacoes_pendentes = reserva.consumacoes.filter(pago=False)
    
    total_pendente = sum(c.valor_total for c in consumacoes_pendentes)
    
    if total_pendente <= 0:
        return redirect('gerenciar_consumacao', reserva_id=reserva.id)
        
    sdk = mercadopago.SDK(os.getenv("MERCADO_PAGO_ACCESS_TOKEN"))
    
    preference_data = {
        "items": [
            {
                "id": f"COMBO_{reserva.id}",
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
        # Nova tag exclusiva para avisar o Webhook que é um pagamento em lote
        "external_reference": f"COMBO_{reserva.id}",
        "notification_url": f"{os.getenv('DOMINIO_SISTEMA')}/webhook/mercadopago/",
    }
    
    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]
    
    if preference.get("id"):
        link_combo = preference.get("sandbox_init_point")
        
        # A MÁGICA: Em vez de apagar os itens da tela de pagamentos para agrupar,
        # nós preservamos eles e apenas atualizamos com o link do combo!
        Pagamento.objects.filter(
            reserva=reserva,
            status='PENDENTE',
            id_transacao_externa__startswith="ITEM_CONS_"
        ).update(link_pagamento=link_combo)
        
        return redirect(link_combo)
        
    return redirect('gerenciar_consumacao', reserva_id=reserva.id)

@login_required
def excluir_consumacao(request, consumacao_id):
    """
    Exclui um item da consumação e remove o pagamento espelhado dele (se houver).
    """
    consumacao = get_object_or_404(Consumacao, id=consumacao_id)
    reserva_id = consumacao.reserva.id
    
    if request.method == 'POST':
        # 1. Deleta o espelho dele lá na tabela de pagamentos usando a nossa etiqueta secreta
        Pagamento.objects.filter(
            reserva_id=reserva_id,
            id_transacao_externa=f"ITEM_CONS_{consumacao.id}"
        ).delete()
        
        # 2. Deleta o item da consumação
        consumacao.delete()
        
        # 3. Volta para a tela da reserva
        return redirect('gerenciar_consumacao', reserva_id=reserva_id)
        
    # Se não for POST, renderiza a tela de confirmação
    return render(request, 'consumacao/confirmar_exclusao.html', {'consumacao': consumacao})