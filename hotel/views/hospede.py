from django.shortcuts import render, redirect
from hotel.forms.hospede import HospedeForm

def cadastrar_hospede(request):
    if request.method == 'POST':
        form = HospedeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cadastrar_hospede') # Por enquanto redireciona para o próprio form
    else:
        form = HospedeForm()
    
    return render(request, 'hospedes/form_hospede.html', {'form': form})