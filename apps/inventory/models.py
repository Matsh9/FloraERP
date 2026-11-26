from datetime import timedelta
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from apps.catalog.models import Produto


class Lote(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name="lotes")
    codigo = models.CharField(max_length=80)
    quantidade_inicial = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    quantidade_disponivel = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    data_entrada = models.DateField(default=timezone.localdate)
    data_validade = models.DateField(null=True, blank=True, help_text="Obrigatória em novas entradas; nula somente para saldo legado.")
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    observacao = models.TextField(blank=True)
    legado = models.BooleanField(default=False, editable=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["data_validade", "data_entrada", "id"]
        constraints = [
            models.UniqueConstraint(fields=["produto", "codigo"], name="lote_codigo_unico_produto"),
            models.CheckConstraint(condition=Q(quantidade_inicial__gt=0), name="lote_qtd_inicial_positiva"),
            models.CheckConstraint(condition=Q(quantidade_disponivel__gte=0), name="lote_qtd_disponivel_nao_negativa"),
            models.CheckConstraint(condition=Q(quantidade_disponivel__lte=models.F("quantidade_inicial")), name="lote_saldo_ate_inicial"),
            models.CheckConstraint(condition=Q(custo_unitario__gte=0), name="lote_custo_nao_negativo"),
            models.CheckConstraint(condition=Q(data_validade__isnull=True) | Q(data_validade__gte=models.F("data_entrada")), name="lote_validade_apos_entrada"),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.quantidade_disponivel is not None and self.quantidade_inicial is not None and self.quantidade_disponivel > self.quantidade_inicial:
            raise ValidationError({"quantidade_disponivel": "O saldo não pode superar a quantidade inicial."})
        if self.data_entrada and self.data_entrada > timezone.localdate():
            raise ValidationError({"data_entrada": "A data de entrada não pode estar no futuro."})
        if self.data_validade and self.data_entrada and self.data_validade < self.data_entrada:
            raise ValidationError({"data_validade": "A validade não pode ser anterior à data de entrada."})

    @property
    def situacao(self):
        if self.quantidade_disponivel <= 0:
            return "sem_saldo"
        hoje = timezone.localdate()
        if self.data_validade and self.data_validade < hoje:
            return "vencido"
        if self.data_validade and self.data_validade <= hoje + timedelta(days=30):
            return "proximo_vencimento"
        return "com_saldo"

    def __str__(self):
        return f"{self.produto.nome} — {self.codigo}"


class MovimentacaoEstoque(models.Model):
    TIPOS=[("entrada","Entrada"),("venda","Venda"),("perda","Perda"),("ajuste","Ajuste"),("estorno","Estorno")]
    produto=models.ForeignKey(Produto,on_delete=models.PROTECT,related_name="movimentacoes")
    lote=models.ForeignKey(Lote,on_delete=models.PROTECT,null=True,blank=True,related_name="movimentacoes")
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
