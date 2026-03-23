from django.shortcuts import render, redirect, get_object_or_404
from ..models.quarto import Quarto
from ..forms.quarto import QuartoForm

# --- CREATE ---
def cadastrar_quarto(request):
    if request.method == 'POST':
        form = QuartoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_quartos')
    else:
        form = QuartoForm()
    return render(request, 'quartos/form_quarto.html', {'form': form, 'acao': 'Novo Quarto'})

# --- READ ---
def listar_quartos(request):
    # O order_by('numero') já traz a lista em ordem numérica/alfabética
    quartos = Quarto.objects.all().order_by('numero')
    return render(request, 'quartos/lista_quartos.html', {'quartos': quartos})

# --- UPDATE ---
def editar_quarto(request, id):
    quarto = get_object_or_404(Quarto, id=id)
    if request.method == 'POST':
        form = QuartoForm(request.POST, instance=quarto)
        if form.is_valid():
            form.save()
            return redirect('listar_quartos')
    else:
        form = QuartoForm(instance=quarto)
    return render(request, 'quartos/form_quarto.html', {'form': form, 'acao': 'Editar Quarto'})

# --- DELETE ---
def excluir_quarto(request, id):
    quarto = get_object_or_404(Quarto, id=id)
    if request.method == 'POST':
        quarto.delete()
        return redirect('listar_quartos')
    return render(request, 'quartos/confirmar_exclusao.html', {'quarto': quarto})