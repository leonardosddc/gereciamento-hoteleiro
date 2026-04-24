from django import forms
from hotel.models.consumacao import Consumacao

class ConsumacaoForm(forms.ModelForm):
    class Meta:
        model = Consumacao
        # Não colocamos a 'reserva' aqui porque ela será preenchida automaticamente na View
        fields = ['item', 'quantidade', 'valor_unitario', 'pago']
        
    def clean_valor_unitario(self):
        valor = self.cleaned_data.get('valor_unitario')
        if valor <= 0:
            raise forms.ValidationError("O valor do item deve ser maior que zero.")
        return valor
