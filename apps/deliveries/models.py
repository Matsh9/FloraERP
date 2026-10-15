from django.db import models
from django.conf import settings
from apps.sales.models import Pedido
from apps.customers.models import Cliente
class Entrega(models.Model):
    STATUS=[("agendada","Agendada"),("preparacao","Em preparação"),("saiu","Saiu para entrega"),("entregue","Entregue"),("cancelada","Cancelada")]
    pedido=models.OneToOneField(Pedido,on_delete=models.PROTECT,related_name="entrega")
    cliente=models.ForeignKey(Cliente,on_delete=models.PROTECT)
    telefone=models.CharField(max_length=24)
    cpf=models.CharField(max_length=14,blank=True)
    endereco=models.CharField(max_length=180)
    numero=models.CharField(max_length=20,blank=True)
    complemento=models.CharField(max_length=100,blank=True)
    bairro=models.CharField(max_length=100,blank=True)
    cidade=models.CharField(max_length=100,blank=True)
    estado=models.CharField(max_length=2,blank=True)
    cep=models.CharField(max_length=9,blank=True)
    data_entrega=models.DateField()
    horario_entrega=models.TimeField()
    observacoes=models.TextField(blank=True)
    responsavel=models.CharField(max_length=120,blank=True)
    status=models.CharField(max_length=12,choices=STATUS,default="agendada")
    entregue_em=models.DateTimeField(null=True,blank=True)
    criado_em=models.DateTimeField(auto_now_add=True)
    def clean(self):
        from django.core.exceptions import ValidationError
        from django.utils import timezone
        if self.data_entrega and self.data_entrega < timezone.localdate():
            raise ValidationError({"data_entrega":"Não é possível agendar para uma data passada."})
        if self.status=="entregue" and not self.entregue_em:
            raise ValidationError({"status":"Registre a data e hora de conclusão da entrega."})
