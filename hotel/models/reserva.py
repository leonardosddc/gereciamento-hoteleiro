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
        # 1. Verifica se é uma reserva nova ANTES de salvar
        nova_reserva = self.pk is None
        
        # 2. Lógica de Check-out (muda status do quarto)
        if self.status == self.StatusReserva.CHECK_OUT:
            self.quarto.status = self.quarto.StatusQuarto.SUJO
            self.quarto.save()
            
        # 3. Salva a reserva de fato no banco de dados
        super().save(*args, **kwargs)

        # 4. Gatilho para criar ou atualizar o pagamento da estadia
        from .pagamento import Pagamento 
        
        # --- INÍCIO DO CÁLCULO ---
        # A matemática agora fica de fora do IF, para rodar sempre que salvar
        dias_hospedados = (self.data_checkout - self.data_checkin).days
        if dias_hospedados <= 0:
            dias_hospedados = 1
            
        valor_calculado = dias_hospedados * self.quarto.preco_diaria
        # --- FIM DO CÁLCULO ---
        
        if nova_reserva:
            # Se for nova, cria o pagamento original
            Pagamento.objects.create(
                reserva=self,
                valor_total=valor_calculado,
                status=Pagamento.StatusPagamento.PENDENTE
            )
        else:
            # Se for uma edição, busca o pagamento principal da diária 
            # (que é aquele que não tem etiqueta 'id_transacao_externa' de consumação)
            pagamento_estadia = Pagamento.objects.filter(
                reserva=self,
                id_transacao_externa__isnull=True
            ).first()
            
            # Atualiza o valor apenas se o hóspede ainda não tiver pago (Pendente)
            if pagamento_estadia and pagamento_estadia.status == Pagamento.StatusPagamento.PENDENTE:
                pagamento_estadia.valor_total = valor_calculado
                pagamento_estadia.save()