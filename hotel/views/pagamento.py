import os
import json

import mercadopago

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from ..models.pagamento import Pagamento
from ..forms.pagamento import PagamentoForm
from ..models.reserva import Reserva

# Nova função: Calcula os valores de todas as reservas e transforma em JSON para o JavaScript
def obter_valores_reservas():
    valores = {}
    for reserva in Reserva.objects.all():
        dias = (reserva.data_checkout - reserva.data_checkin).days
        if dias == 0:
            dias = 1
        # Multiplica os dias pelo preço e guarda no dicionário
        valores[reserva.id] = str(dias * reserva.quarto.preco_diaria)
    return json.dumps(valores)

# --- CREATE ---
def cadastrar_pagamento(request):
    if request.method == 'POST':
        form = PagamentoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_pagamentos')
    else:
        form = PagamentoForm()
    
    # Adicionamos os valores no 'contexto' para enviar ao HTML
    contexto = {
        'form': form, 
        'acao': 'Novo Pagamento',
        'valores_json': obter_valores_reservas()
    }
    return render(request, 'pagamentos/form_pagamento.html', contexto)

# --- READ ---
def listar_pagamentos(request):
    pagamentos = Pagamento.objects.all().select_related('reserva__hospede', 'reserva__quarto').order_by('-id')
    return render(request, 'pagamentos/lista_pagamentos.html', {'pagamentos': pagamentos})

# --- UPDATE ---
def editar_pagamento(request, id):
    pagamento = get_object_or_404(Pagamento, id=id)
    if request.method == 'POST':
        form = PagamentoForm(request.POST, instance=pagamento)
        if form.is_valid():
            form.save()
            return redirect('listar_pagamentos')
    else:
        form = PagamentoForm(instance=pagamento)
        
    contexto = {
        'form': form, 
        'acao': 'Editar Pagamento',
        'valores_json': obter_valores_reservas()
    }
    return render(request, 'pagamentos/form_pagamento.html', contexto)

# --- DELETE ---
def excluir_pagamento(request, id):
    pagamento = get_object_or_404(Pagamento, id=id)
    if request.method == 'POST':
        pagamento.delete()
        return redirect('listar_pagamentos')
    return render(request, 'pagamentos/confirmar_exclusao.html', {'pagamento': pagamento})

def gerar_link_pagamento(request, pagamento_id):
    pagamento = get_object_or_404(Pagamento, id=pagamento_id)
    reserva = pagamento.reserva
    
    # 1. Configura o Mercado Pago
    sdk = mercadopago.SDK(os.getenv("MERCADO_PAGO_ACCESS_TOKEN"))

    # 2. Monta o pacote de dados da 'Preferência' (Checkout Pro)
    preference_data = {
        "items": [
            {
                "id": str(pagamento.id),
                "title": f"Reserva {reserva.id} - Quarto {reserva.quarto.numero}",
                "description": f"Hóspede: {reserva.hospede.nome}",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": float(pagamento.valor_total),
            }
        ],
        "payer": {
            "name": reserva.hospede.nome,
            "email": reserva.hospede.email,
            "identification": {
                "type": "CPF",
                "number": reserva.hospede.cpf
            },
        },
        # Você pode referenciar o ID externo aqui para facilitar a busca no webhook
        "external_reference": str(pagamento.id),
    }

    # 3. Faz a requisição para criar o Link
    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]

    # 4. Salva a URL no banco de dados
    if preference.get("id"):
        pagamento.id_transacao_externa = preference["id"]
        # Usamos o 'sandbox_init_point' porque estamos no ambiente de testes do TCC!
        # Na vida real (produção), usaríamos apenas 'init_point'
        pagamento.link_pagamento = preference["sandbox_init_point"] 
        pagamento.save()
    
    return redirect('listar_pagamentos')

# SUBSTITUA SEU WEBHOOK POR ESTE:
@csrf_exempt
def webhook_mercado_pago(request):
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            
            # O Mercado Pago pode enviar 'action' ou 'type' dependendo da versão configurada
            if dados.get("action") == "payment.updated" or dados.get("type") == "payment":
                id_pagamento_mp = dados.get("data", {}).get("id")
                
                if id_pagamento_mp:
                    # 1. Pergunta para o Mercado Pago os detalhes desse pagamento
                    sdk = mercadopago.SDK(os.getenv("MERCADO_PAGO_ACCESS_TOKEN"))
                    payment_info = sdk.payment().get(id_pagamento_mp)
                    
                    if payment_info["status"] == 200:
                        info = payment_info["response"]
                        
                        # 2. Pega a "etiqueta" (external_reference) e o status real
                        pagamento_id_interno = info.get("external_reference")
                        status_pagamento = info.get("status")
                        
                        # 3. Se foi aprovado, atualiza no nosso banco de dados
                        if pagamento_id_interno and status_pagamento == 'approved':
                            pagamento = Pagamento.objects.filter(id=pagamento_id_interno).first()
                            
                            if pagamento and pagamento.status != 'CONCLUIDO':
                                pagamento.status = 'CONCLUIDO'
                                pagamento.data_pagamento = timezone.now()
                                pagamento.save()
                                
            return JsonResponse({"status": "sucesso"}, status=200)
        except Exception as e:
            return JsonResponse({"erro": str(e)}, status=400)
            
    return JsonResponse({"erro": "Método não permitido"}, status=405)