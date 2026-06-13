from datetime import date, timedelta
from django import forms
from hotel.models.reserva import Reserva

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['hospede', 'quarto', 'data_checkin', 'data_checkout', 'status']
        widgets = {
            'data_checkin': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'data_checkout': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            if 'status' in self.fields:
                del self.fields['status']

    def clean(self):
        cleaned_data = super().clean()
        data_checkin = cleaned_data.get("data_checkin")
        data_checkout = cleaned_data.get("data_checkout")
        status = cleaned_data.get("status")
        quarto = cleaned_data.get("quarto")
        hoje = date.today()

        if data_checkin and data_checkout:
            if data_checkin < hoje:
                self.add_error('data_checkin', "O Check-in não pode ser feito em uma data no passado.")

            limite_futuro = hoje + timedelta(days=365 * 3)
            if data_checkin > limite_futuro:
                self.add_error('data_checkin', "Não é possível agendar reservas com mais de 3 anos de antecedência.")

            if data_checkout <= data_checkin:
                self.add_error('data_checkout', "A data de Check-out deve ser posterior à de Check-in.")
            else:
                limite_estadia = timedelta(days=180)
                if (data_checkout - data_checkin) > limite_estadia:
                    self.add_error('data_checkout', "A estadia não pode ultrapassar o limite de 6 meses (180 dias).")

            # --- TRAVA DE OVERBOOKING (RF05) ---
            if quarto:
                # Busca se o mesmo quarto já tem reservas ativas no período selecionado
                reservas_conflitantes = Reserva.objects.filter(
                    quarto=quarto,
                    status__in=['AGENDADA', 'CHECK_IN']
                ).filter(
                    data_checkin__lt=data_checkout,  # Check-in existente antes do novo Check-out
                    data_checkout__gt=data_checkin   # Check-out existente depois do novo Check-in
                )

                # Se estivermos EDITANDO uma reserva antiga, não deixamos ela conflitar com ela mesma
                if self.instance.pk:
                    reservas_conflitantes = reservas_conflitantes.exclude(pk=self.instance.pk)

                # Se houver conflitos de agenda, exibe o erro na tela anexado ao campo do Quarto
                if reservas_conflitantes.exists():
                    self.add_error('quarto', "Overbooking blocked! Este quarto já possui uma reserva ativa para esse período.")

        # --- REGRAS DE NEGÓCIO DO TCC (Trava de Status) ---
        if self.instance.pk: # Se a reserva já existe no banco...
            
            # REGRA 1: Bloqueia Check-in se a diária não estiver paga
            if status == 'CHECK_IN':
                pagamento_ok = self.instance.pagamentos.filter(status='CONCLUIDO').exists()
                if not pagamento_ok:
                    self.add_error('status', "Check-in bloqueado: O pagamento da estadia ainda não foi concluído.")
            
            # REGRA 2: Bloqueia Check-out se houver consumação pendente OU se não tiver feito Check-in
            if status == 'CHECK_OUT':
                
                # --- NOVA TRAVA DE ESTADO ---
                # Se o status atual no banco é Agendada, ele não pode pular para Check-out
                if self.instance.status == 'AGENDADA':
                    self.add_error('status', "Operação inválida: Não é possível fazer Check-out sem antes realizar o Check-in do hóspede.")
                # -----------------------------
                
                consumacoes_pendentes = self.instance.consumacoes.filter(pago=False)
                if consumacoes_pendentes.exists():
                    total_devendo = sum(c.valor_total for c in consumacoes_pendentes)
                    self.add_error('status', f"Check-out bloqueado: O hóspede possui R$ {total_devendo:.2f} em consumação pendente.")

        return cleaned_data