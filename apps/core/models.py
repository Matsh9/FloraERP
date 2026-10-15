from django.conf import settings
from django.db import models
class RegistroAuditoria(models.Model):
    usuario=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL)
    acao=models.CharField(max_length=100)
    entidade=models.CharField(max_length=100,blank=True)
    entidade_id=models.CharField(max_length=64,blank=True)
    detalhes=models.TextField(blank=True)
    criado_em=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=["-criado_em"]
    def __str__(self): return f"{self.acao} — {self.criado_em:%d/%m/%Y %H:%M}"
