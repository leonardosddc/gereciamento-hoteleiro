from django import forms
from hotel.models.quarto import Quarto

class QuartoForm(forms.ModelForm):
    class Meta:
        model = Quarto
        fields = ['numero', 'tipo', 'status', 'preco_diaria']

    def clean_preco_diaria(self):
        preco = self.cleaned_data.get('preco_diaria')
        if preco <= 0:
            raise forms.ValidationError("O preço da diária deve ser maior que zero.")
        return preco
        
    def clean_numero(self):
        numero = self.cleaned_data.get('numero')
        # Salva o número sempre em maiúsculo (caso use letras, ex: 10A)
        return numero.upper()