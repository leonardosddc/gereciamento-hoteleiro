from datetime import date, timedelta
from django import forms
from hotel.models.reserva import Reserva

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['hospede', 'quarto', 'data_checkin', 'data_checkout', 'status']
        widgets = {
            'data_checkin': forms.DateInput(attrs={'type': 'date'}),
            'data_checkout': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        data_checkin = cleaned_data.get("data_checkin")
        data_checkout = cleaned_data.get("data_checkout")

        # Pega a data atual do servidor
        hoje = date.today()

        if data_checkin and data_checkout:
            
            # 1. Valida se o check-in é uma data passada
            if data_checkin < hoje:
                self.add_error('data_checkin', "O Check-in não pode ser feito em uma data no passado.")

            # 2. NOVA VALIDAÇÃO: Impede check-in absurdamente distante (Máximo de 3 anos)
            # 3 anos = aproximadamente 1095 dias (365 * 3)
            limite_futuro = hoje + timedelta(days=365 * 3)
            if data_checkin > limite_futuro:
                self.add_error('data_checkin', "Não é possível agendar reservas com mais de 3 anos de antecedência.")

            # 3. Valida se o check-out não é anterior ou igual ao check-in
            if data_checkout <= data_checkin:
                self.add_error('data_checkout', "A data de Check-out deve ser posterior à de Check-in.")
            else:
                # 4. Valida o limite máximo de 6 meses de estadia
                limite_estadia = timedelta(days=180)
                if (data_checkout - data_checkin) > limite_estadia:
                    self.add_error('data_checkout', "A estadia não pode ultrapassar o limite de 6 meses (180 dias).")

        return cleaned_data