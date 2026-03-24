from django import forms
from django.utils import timezone
from hotel.models.pagamento import Pagamento
from datetime import timedelta


class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = ['reserva', 'valor_total', 'metodo', 'status', 'data_pagamento']
        widgets = {
            'data_pagamento': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_valor_total(self):
        valor = self.cleaned_data.get('valor_total')
        if valor is not None and valor <= 0:
            raise forms.ValidationError("O valor do pagamento deve ser maior que zero.")
        return valor

    def clean(self):
        cleaned_data = super().clean()
        reserva = cleaned_data.get('reserva')
        valor_total = cleaned_data.get('valor_total')
        status = cleaned_data.get('status')
        data_pagamento = cleaned_data.get('data_pagamento')

        # 1. Validações de Status e Data (Preenchimento)
        if status == 'CONCLUIDO' and not data_pagamento:
            self.add_error('data_pagamento', "É obrigatório informar a data e hora para pagamentos concluídos.")
        
        if status == 'PENDENTE' and data_pagamento:
            self.add_error('data_pagamento', "Pagamentos pendentes não devem ter data de pagamento.")

        # 2. VALIDAÇÃO: Lógica de Datas
        if status == 'CONCLUIDO' and data_pagamento and reserva:
            agora = timezone.now()
            
            # Regra A: O pagamento não pode ocorrer antes da reserva existir no sistema
            if data_pagamento < reserva.criada_em:
                self.add_error('data_pagamento', "O pagamento não pode ter ocorrido antes da reserva ser criada.")

            # Regra B (A SUA REGRA!): Pagamento TEM que ser antes ou no máximo no dia do Check-in
            # Usamos .date() porque data_pagamento tem hora, e data_checkin não.
            if data_pagamento.date() > reserva.data_checkin:
                self.add_error(
                    'data_pagamento', 
                    f"O pagamento deve ser concluído até a data do Check-in ({reserva.data_checkin.strftime('%d/%m/%Y')}). Ninguém entra sem pagar! 😉"
                )

        # 3. Validação: Consistência Matemática do Valor
        if reserva and valor_total:
            dias_estadia = (reserva.data_checkout - reserva.data_checkin).days
            if dias_estadia == 0:
                dias_estadia = 1 
            
            valor_esperado = dias_estadia * reserva.quarto.preco_diaria

            if valor_total < valor_esperado:
                self.add_error(
                    'valor_total', 
                    f"Inconsistência! A reserva tem {dias_estadia} diária(s) a R$ {reserva.quarto.preco_diaria}. O valor deve ser no mínimo R$ {valor_esperado}."
                )

        return cleaned_data