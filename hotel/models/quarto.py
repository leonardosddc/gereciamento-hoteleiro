from django.db import models


class Quarto(models.Model):
    class TipoQuarto(models.TextChoices):
        SOLTEIRO = 'SOLTEIRO', 'Solteiro'
        CASAL = 'CASAL', 'Casal'
        FAMILIA = 'FAMILIA', 'Família'

    class StatusQuarto(models.TextChoices):
        LIMPO = 'LIMPO', 'Limpo'
        SUJO = 'SUJO', 'Sujo'
        MANUTENCAO = 'MANUTENCAO', 'Manutenção'
        OCUPADO = 'OCUPADO', 'Ocupado'

    numero = models.CharField(max_length=10, unique=True)
    
    tipo = models.CharField(
        max_length=20,
        choices=TipoQuarto.choices,
        default=TipoQuarto.SOLTEIRO
    )
    
    status = models.CharField(
        max_length=20,
        choices=StatusQuarto.choices,
        default=StatusQuarto.LIMPO
    )
    
    preco_diaria = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Quarto {self.numero} ({self.tipo})"