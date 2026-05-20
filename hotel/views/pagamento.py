import os
import json

import mercadopago

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from ..models.pagamento import Pagamento
from ..forms.pagamento import PagamentoForm
from ..models.reserva import Reserva

# RECORREÇÃO: Removeu-se o @login_required daqui (é uma função auxiliar)
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
@login_required
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
@login_required
def listar_pagamentos(request):
    pagamentos = Pagamento.objects.all().select_related('reserva__hospede', 'reserva__quarto').order_by('-id')
    return render(request, 'pagamentos/lista_pagamentos.html', {'pagamentos': pagamentos})

# --- UPDATE ---
@login_required
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
@login_required
def excluir_pagamento(request, id):
    pagamento = get_object_or_404(Pagamento, id=id)
    if request.method == 'POST':
        pagamento.delete()
        return redirect('listar_pagamentos')
    return render(request, 'pagamentos/confirmar_exclusao.html', {'pagamento': pagamento})

@login_required
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
        "external_reference": str(pagamento.id),
        "notification_url": "https://sprint-ladder-steadily.ngrok-free.dev/webhook/mercadopago/",
    }
    # 3. Faz a requisição para criar o Link
    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]

    # 4. Salva a URL no banco de dados
    if preference.get("id"):
        pagamento.id_transacao_externa = preference["id"]
        pagamento.link_pagamento = preference["sandbox_init_point"] 
        pagamento.save()
    
    return redirect('listar_pagamentos')

# RECORREÇÃO: Removeu-se o @login_required daqui também (é uma função auxiliar)
def traduzir_metodo_pagamento(mp_method_id):
    """ Mapeia o retorno de texto do Mercado Pago para os Choices do seu Model """
    method = str(mp_method_id).lower()
    if 'pix' in method:
        return 'PIX'
    elif 'ticket' in method or 'bolbradesco' in method:
        return 'BOLETO_BANCARIO'
    elif 'debit' in method:
        return 'CARTAO_DEBITO'
    else:
        return 'CARTAO_CREDITO'

# O Webhook continua sem @login_required para permitir o acesso do bot do Mercado Pago
@csrf_exempt
def webhook_mercado_pago(request):
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            
            if dados.get("action") == "payment.updated" or dados.get("type") == "payment":
                id_pagamento_mp = dados.get("data", {}).get("id")
                
                if id_pagamento_mp:
                    sdk = mercadopago.SDK(os.getenv("MERCADO_PAGO_ACCESS_TOKEN"))
                    payment_info = sdk.payment().get(id_pagamento_mp)
                    
                    if payment_info["status"] == 200:
                        info = payment_info["response"]
                        
                        pagamento_id_interno = info.get("external_reference")
                        status_pagamento = info.get("status")
                        
                        metodo_utilizado_mp = info.get("payment_method_id")
                        metodo_convertido = traduzir_metodo_pagamento(metodo_utilizado_mp)
                        
                        if pagamento_id_interno and status_pagamento == 'approved':
                            
                            if str(pagamento_id_interno).startswith("CONSUMACAO_"):
                                pk_real = pagamento_id_interno.split("_")[1]
                                pagamento = Pagamento.objects.filter(id=pk_real).first()
                            
                                if pagamento and pagamento.status != 'CONCLUIDO':
                                    pagamento.status = 'CONCLUIDO'
                                    pagamento.metodo = metodo_convertido
                                    pagamento.data_pagamento = timezone.now()
                                    pagamento.save()

                                    pagamento.reserva.consumacoes.filter(pago=False).update(pago=True)
                            
                            else:
                                pagamento = Pagamento.objects.filter(id=pagamento_id_interno).first()

                                if pagamento and pagamento.status != 'CONCLUIDO':
                                    pagamento.status = 'CONCLUIDO'
                                    pagamento.metodo = metodo_convertido
                                    pagamento.data_pagamento = timezone.now()
                                    pagamento.save()
                                
            return JsonResponse({"status": "sucesso"}, status=200)
        except Exception as e:
            return JsonResponse({"erro": str(e)}, status=400)
            
    return JsonResponse({"erro": "Método não permitido"}, status=405)