import json
from django.shortcuts import render, redirect, get_object_or_404
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