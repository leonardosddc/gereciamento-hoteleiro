from django.db import models
from .hospede import Hospede
from .quarto import Quarto


class Reserva(models.Model):
    class StatusReserva(models.TextChoices):
        AGENDADA = 'AGENDADA', 'Agendada'
        CHECK_IN = 'CHECK_IN', 'Check-in'
        CHECK_OUT = 'CHECK_OUT', 'Check-out'
        CANCELADA = 'CANCELADA', 'Cancelada'

    hospede = models.ForeignKey(Hospede, on_delete=models.CASCADE, related_name='reservas')
    quarto = models.ForeignKey(Quarto, on_delete=models.PROTECT, related_name='reservas')

    data_checkin = models.DateField()
    data_checkout = models.DateField()
    status = models.CharField(
        max_length=20, 
        choices=StatusReserva.choices, 
        default=StatusReserva.AGENDADA
    )
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reserva {self.id} - {self.hospede.nome}"
    
    def save(self, *args, **kwargs):
        # 1. Verifica se é uma reserva nova
        nova_reserva = self.pk is None
        
        # 2. Lógica existente de Check-out
        if self.status == self.StatusReserva.CHECK_OUT:
            self.quarto.status = self.quarto.StatusQuarto.SUJO
            self.quarto.save()
            
        # 3. Salva a reserva de fato no banco de dados
        super().save(*args, **kwargs)

        # 4. Gatilho automático para criar o pagamento com cálculo real
        if nova_reserva:
            from .pagamento import Pagamento 
            
            # --- INÍCIO DO CÁLCULO ---
            # Descobre a quantidade de dias da reserva
            dias_hospedados = (self.data_checkout - self.data_checkin).days
            
            # Regra de segurança: se o hóspede entra e sai no mesmo dia, cobra pelo menos 1 diária
            if dias_hospedados <= 0:
                dias_hospedados = 1
                
            # Multiplica os dias pelo valor da diária do quarto
            # ATENÇÃO: Verifique se o nome do campo no seu model Quarto é 'valor_diaria' mesmo!
            valor_calculado = dias_hospedados * self.quarto.preco_diaria
            # --- FIM DO CÁLCULO ---
            
            Pagamento.objects.create(
                reserva=self,
                valor_total=valor_calculado,
                status=Pagamento.StatusPagamento.PENDENTE
            )