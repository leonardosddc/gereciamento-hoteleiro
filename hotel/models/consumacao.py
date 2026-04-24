from django.db import models
from .reserva import Reserva

class Consumacao(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='consumacoes')
    item = models.CharField(max_length=100)
    quantidade = models.PositiveIntegerField(default=1)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    pago = models.BooleanField(default=False)
    data_lancamento = models.DateTimeField(auto_now_add=True)

    @property
    def valor_total(self):
        return self.quantidade * self.valor_unitario

    def __str__(self):
        return f"{self.quantidade}x {self.item} - Reserva {self.reserva.id}"
