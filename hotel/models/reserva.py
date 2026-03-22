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