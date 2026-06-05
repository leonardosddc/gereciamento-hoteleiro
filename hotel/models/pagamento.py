from django.db import models
from .reserva import Reserva


class Pagamento(models.Model):
    class MetodoPagamento(models.TextChoices):
        PIX = 'PIX', 'Pix'
        CARTAO_CREDITO = 'CARTAO_CREDITO', 'Cartão de Crédito'
        CARTAO_DEBITO = 'CARTAO_DEBITO', 'Cartão de Débito'
        BOLETO_BANCARIO = 'BOLETO_BANCARIO', 'Boleto Bancário'
        DINHEIRO = 'DINHEIRO', 'Dinheiro'

    class StatusPagamento(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        CONCLUIDO = 'CONCLUIDO', 'Concluído'
        ESTORNADO = 'ESTORNADO', 'Estornado'


    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='pagamentos')

    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    data_pagamento = models.DateTimeField(null=True, blank=True)
    metodo = models.CharField(max_length=30, choices=MetodoPagamento.choices, null=True, blank=True)
    status = models.CharField(
        max_length=20, 
        choices=StatusPagamento.choices, 
        default=StatusPagamento.PENDENTE
    )

    id_transacao_externa = models.CharField(max_length=100, null=True, blank=True)
    link_pagamento = models.URLField(null=True, blank=True)

    @property
    def descricao(self):
        # Se a etiqueta começar com ITEM_CONS_, é um item individual da consumação
        if self.id_transacao_externa and str(self.id_transacao_externa).startswith('ITEM_CONS_'):
            try:
                # Extrai o número do ID do final da etiqueta
                cons_id = str(self.id_transacao_externa).split('_')[-1]
                # Importação local para evitar erro de referência circular
                from .consumacao import Consumacao 
                item_consumido = Consumacao.objects.get(id=cons_id)
                return f"{item_consumido.quantidade}x {item_consumido.item}"
            except:
                return "Item excluído"
                
        # Se começar com CONSUMACAO_, é aquele combo gerado pelo botão Pagar Online
        elif self.id_transacao_externa and str(self.id_transacao_externa).startswith('CONSUMACAO_'):
            return "Vários itens (Pagar Online)"
            
        # Se não tiver etiqueta, assumimos que é o pagamento principal da diária
        return "Estadia"

    def __str__(self):
        return f"Pagamento {self.id} - {self.status}"