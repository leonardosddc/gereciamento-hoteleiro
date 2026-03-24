from django.shortcuts import render, redirect, get_object_or_404
from ..models.reserva import Reserva
from ..forms.reserva import ReservaForm

# --- CREATE ---
def cadastrar_reserva(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_reservas')
    else:
        form = ReservaForm()
    return render(request, 'reservas/form_reserva.html', {'form': form, 'acao': 'Nova Reserva'})

# --- READ ---
def listar_reservas(request):
    # O select_related ajuda na performance quando temos Chaves Estrangeiras (ForeignKey)
    reservas = Reserva.objects.all().select_related('hospede', 'quarto').order_by('data_checkin')
    return render(request, 'reservas/lista_reservas.html', {'reservas': reservas})

# --- UPDATE ---
def editar_reserva(request, id):
    reserva = get_object_or_404(Reserva, id=id)
    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            return redirect('listar_reservas')
    else:
        form = ReservaForm(instance=reserva)
    return render(request, 'reservas/form_reserva.html', {'form': form, 'acao': 'Editar Reserva'})

# --- DELETE ---
def excluir_reserva(request, id):
    reserva = get_object_or_404(Reserva, id=id)
    if request.method == 'POST':
        reserva.delete()
        return redirect('listar_reservas')
    return render(request, 'reservas/confirmar_exclusao.html', {'reserva': reserva})