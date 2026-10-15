from django.conf import settings
from django.db import models
from apps.catalog.models import Produto
class MovimentacaoEstoque(models.Model):
    TIPOS=[("entrada","Entrada"),("venda","Venda"),("perda","Perda"),("ajuste","Ajuste"),("estorno","Estorno")]
    produto=models.ForeignKey(Produto,on_delete=models.PROTECT,related_name="movimentacoes")
    tipo=models.CharField(max_length=12,choices=TIPOS)
    quantidade=models.DecimalField(max_digits=10,decimal_places=2,help_text="Quantidade positiva; o tipo define o efeito.")
    saldo_anterior=models.DecimalField(max_digits=10,decimal_places=2)
    saldo_posterior=models.DecimalField(max_digits=10,decimal_places=2)
    referencia=models.CharField(max_length=120,blank=True)
    observacao=models.TextField(blank=True)
    usuario=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,on_delete=models.SET_NULL)
    criado_em=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=["-criado_em"]
class PerdaEstoque(models.Model):
    MOTIVOS=[("danificado","Danificado"),("murcho","Murcho"),("quebrado","Quebrado"),("vencido","Vencido"),("outro","Outro")]
    produto=models.ForeignKey(Produto,on_delete=models.PROTECT)
    quantidade=models.DecimalField(max_digits=10,decimal_places=2)
    motivo=models.CharField(max_length=20,choices=MOTIVOS)
    observacao=models.TextField(blank=True)
    custo_estimado=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    usuario=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,on_delete=models.SET_NULL)
    criado_em=models.DateTimeField(auto_now_add=True)
    movimentacao=models.OneToOneField(MovimentacaoEstoque,null=True,blank=True,on_delete=models.PROTECT)
