import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum

from apps.customers.models import Cliente


FORMA_PAGAMENTO_CHOICES = [
    ("pix", "Pix"),
    ("dinheiro", "Dinheiro"),
    ("credito", "Cartão de crédito"),
    ("debito", "Cartão de débito"),
    ("misto", "Misto"),
]


class Pedido(models.Model):
    STATUS=[("aberto","Aberto"),("concluido","Concluído"),("cancelado","Cancelado")]
    PAGAMENTOS = FORMA_PAGAMENTO_CHOICES
    numero=models.UUIDField(default=uuid.uuid4,unique=True,editable=False)
    cliente=models.ForeignKey(Cliente,null=True,blank=True,on_delete=models.SET_NULL,related_name="pedidos")
    atendente=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,on_delete=models.SET_NULL)
    status=models.CharField(max_length=12,choices=STATUS,default="aberto")
    forma_pagamento=models.CharField(max_length=12,choices=PAGAMENTOS,blank=True)
    desconto=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    subtotal=models.DecimalField(max_digits=12,decimal_places=2,default=0)
    total=models.DecimalField(max_digits=12,decimal_places=2,default=0)
    observacoes=models.TextField(blank=True)
    criado_em=models.DateTimeField(auto_now_add=True)
    concluido_em=models.DateTimeField(null=True,blank=True)
    cancelado_em=models.DateTimeField(null=True,blank=True)

    class Meta: ordering=["-criado_em"]

    def __str__(self):
        return f"Pedido {self.numero}"

    @property
    def total_pago(self):
        total = self.pagamentos.aggregate(total=Sum("valor"))["total"] or Decimal("0")
        return Decimal(total)

    @property
    def valor_pago(self):
        return self.total_pago

    @property
    def valor_restante(self):
        return max(self.total - self.total_pago, Decimal("0"))

    @property
    def valor_pendente(self):
        return self.valor_restante

    @property
    def saldo_pendente(self):
        return self.valor_restante

    @property
    def esta_pago(self):
        return self.total_pago >= self.total

    def registrar_pagamento(self, forma, valor, referencia="", *, save=True):
        if self.status == "cancelado":
            raise ValidationError("Pedido cancelado não pode receber pagamento.")

        if forma not in dict(self.PAGAMENTOS):
            raise ValidationError("Forma de pagamento inválida.")

        valor_decimal = Decimal(str(valor))
        if valor_decimal <= 0:
            raise ValidationError("Valor do pagamento deve ser maior que zero.")

        if self.total_pago + valor_decimal > self.total + Decimal("0.01"):
            raise ValidationError("O valor recebido no pedido não pode exceder o total da venda.")

        pagamento = self.pagamentos.create(forma=forma, valor=valor_decimal, referencia=referencia)
        if self.forma_pagamento and self.forma_pagamento not in {forma, "misto"}:
            self.forma_pagamento = "misto"
        elif not self.forma_pagamento:
            self.forma_pagamento = forma
        if save:
            self.save(update_fields=["forma_pagamento"])
        return pagamento


class ItemPedido(models.Model):
    pedido=models.ForeignKey(Pedido,on_delete=models.PROTECT,related_name="itens")
    produto=models.ForeignKey("catalog.Produto",null=True,blank=True,on_delete=models.PROTECT)
    kit=models.ForeignKey("catalog.Kit",null=True,blank=True,on_delete=models.PROTECT)
    nome_item=models.CharField(max_length=180)
    quantidade=models.DecimalField(max_digits=8,decimal_places=2)
    preco_unitario=models.DecimalField(max_digits=10,decimal_places=2)
    total=models.DecimalField(max_digits=12,decimal_places=2)


class Pagamento(models.Model):
    FORMA_CHOICES = [
        ("pix", "Pix"),
        ("dinheiro", "Dinheiro"),
        ("credito", "Cartão de crédito"),
        ("debito", "Cartão de débito"),
    ]
    pedido=models.ForeignKey(Pedido,on_delete=models.PROTECT,related_name="pagamentos")
    forma=models.CharField(max_length=20,choices=FORMA_CHOICES)
    valor=models.DecimalField(max_digits=12,decimal_places=2)
    referencia=models.CharField(max_length=120,blank=True)
    criado_em=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=["-criado_em"]

    def __str__(self):
        return f"{self.get_forma_display()} - R$ {self.valor}"
