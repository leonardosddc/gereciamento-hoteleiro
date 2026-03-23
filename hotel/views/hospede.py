from django.shortcuts import render, redirect, get_object_or_404
from ..models.hospede import Hospede
from ..forms.hospede import HospedeForm

# --- CREATE (Cadastrar Hóspede) ---
def cadastrar_hospede(request):
    if request.method == 'POST':
        form = HospedeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_hospedes')
    else:
        form = HospedeForm()
    return render(request, 'hospedes/form_hospede.html', {'form': form})

# --- READ (Listar Hóspedes) ---
def listar_hospedes(request):
    hospedes = Hospede.objects.all()
    return render(request, 'hospedes/lista_hospedes.html', {'hospedes': hospedes})

# --- UPDATE (Editar Hóspede) ---
def editar_hospede(request, id):
    hospede = get_object_or_404(Hospede, id=id)
    
    if request.method == 'POST':
        form = HospedeForm(request.POST, instance=hospede)
        if form.is_valid():
            form.save()
            return redirect('listar_hospedes')
    else:
        form = HospedeForm(instance=hospede)
        
    return render(request, 'hospedes/form_hospede.html', {'form': form})

# --- DELETE (Excluir Hóspede) ---
def excluir_hospede(request, id):
    hospede = get_object_or_404(Hospede, id=id)
    
    if request.method == 'POST':
        hospede.delete()
        return redirect('listar_hospedes')
        
    return render(request, 'hospedes/confirmar_exclusao.html', {'hospede': hospede})