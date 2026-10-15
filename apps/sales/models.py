import uuid
from django.conf import settings
from django.db import models
from apps.customers.models import Cliente
class Pedido(models.Model):
    STATUS=[("aberto","Aberto"),("concluido","Concluído"),("cancelado","Cancelado")]
    PAGAMENTOS=[("pix","Pix"),("dinheiro","Dinheiro"),("credito","Cartão de crédito"),("debito","Cartão de débito"),("misto","Misto")]
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
class ItemPedido(models.Model):
    pedido=models.ForeignKey(Pedido,on_delete=models.PROTECT,related_name="itens")
    produto=models.ForeignKey("catalog.Produto",null=True,blank=True,on_delete=models.PROTECT)
    kit=models.ForeignKey("catalog.Kit",null=True,blank=True,on_delete=models.PROTECT)
    nome_item=models.CharField(max_length=180)
    quantidade=models.DecimalField(max_digits=8,decimal_places=2)
    preco_unitario=models.DecimalField(max_digits=10,decimal_places=2)
    total=models.DecimalField(max_digits=12,decimal_places=2)
class Pagamento(models.Model):
    pedido=models.ForeignKey(Pedido,on_delete=models.PROTECT,related_name="pagamentos")
    forma=models.CharField(max_length=20,choices=[("pix","Pix"),("dinheiro","Dinheiro"),("credito","Cartão de crédito"),("debito","Cartão de débito")])
    valor=models.DecimalField(max_digits=12,decimal_places=2)
    referencia=models.CharField(max_length=120,blank=True)
    criado_em=models.DateTimeField(auto_now_add=True)
