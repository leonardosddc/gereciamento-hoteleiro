from django import forms
from hotel.models.pagamento import Pagamento

class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = ['reserva', 'valor_total', 'metodo', 'status', 'data_pagamento']
        widgets = {
            # type="datetime-local" permite escolher data e hora no navegador
            'data_pagamento': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_valor_total(self):
        valor = self.cleaned_data.get('valor_total')
        if valor is not None and valor <= 0:
            raise forms.ValidationError("O valor do pagamento deve ser maior que zero.")
        return valor

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        data_pagamento = cleaned_data.get('data_pagamento')

        # Se o pagamento está concluído, ele OBRIGATORIAMENTE precisa de uma data
        if status == 'CONCLUIDO' and not data_pagamento:
            self.add_error('data_pagamento', "É obrigatório informar a data e hora para pagamentos concluídos.")
        
        # Se está pendente, não faz sentido ter data de pagamento preenchida
        if status == 'PENDENTE' and data_pagamento:
            self.add_error('data_pagamento', "Pagamentos pendentes não devem ter data de pagamento.")

        return cleaned_data