from django.shortcuts import render, redirect, get_object_or_404
from ..models.pagamento import Pagamento
from ..forms.pagamento import PagamentoForm

def cadastrar_pagamento(request):
    if request.method == 'POST':
        form = PagamentoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_pagamentos')
    else:
        form = PagamentoForm()
    return render(request, 'pagamentos/form_pagamento.html', {'form': form, 'acao': 'Novo Pagamento'})

def listar_pagamentos(request):
    # select_related com 'reserva__hospede' ajuda o banco a buscar as informações mais rápido
    pagamentos = Pagamento.objects.all().select_related('reserva__hospede', 'reserva__quarto').order_by('-id')
    return render(request, 'pagamentos/lista_pagamentos.html', {'pagamentos': pagamentos})

def editar_pagamento(request, id):
    pagamento = get_object_or_404(Pagamento, id=id)
    if request.method == 'POST':
        form = PagamentoForm(request.POST, instance=pagamento)
        if form.is_valid():
            form.save()
            return redirect('listar_pagamentos')
    else:
        form = PagamentoForm(instance=pagamento)
    return render(request, 'pagamentos/form_pagamento.html', {'form': form, 'acao': 'Editar Pagamento'})

def excluir_pagamento(request, id):
    pagamento = get_object_or_404(Pagamento, id=id)
    if request.method == 'POST':
        pagamento.delete()
        return redirect('listar_pagamentos')
    return render(request, 'pagamentos/confirmar_exclusao.html', {'pagamento': pagamento})