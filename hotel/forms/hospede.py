from django import forms
from hotel.models.hospede import Hospede

class HospedeForm(forms.ModelForm):
    class Meta:
        model = Hospede
        fields = ['nome', 'cpf', 'data_nascimento', 'email', 'telefone']