from django.db import models
class Cliente(models.Model):
    nome=models.CharField(max_length=160)
    cpf=models.CharField(max_length=14,blank=True,db_index=True)
    telefone=models.CharField(max_length=24)
    whatsapp=models.CharField(max_length=24,blank=True)
    email=models.EmailField(blank=True)
    data_nascimento=models.DateField(null=True,blank=True)
    endereco=models.CharField(max_length=180,blank=True)
    numero=models.CharField(max_length=20,blank=True)
    complemento=models.CharField(max_length=100,blank=True)
    bairro=models.CharField(max_length=100,blank=True)
    cidade=models.CharField(max_length=100,blank=True)
    estado=models.CharField(max_length=2,blank=True)
    cep=models.CharField(max_length=9,blank=True)
    preferencias=models.TextField(blank=True)
    observacoes=models.TextField(blank=True)
    ativo=models.BooleanField(default=True)
    criado_em=models.DateTimeField(auto_now_add=True)
    atualizado_em=models.DateTimeField(auto_now=True)
    class Meta: ordering=["nome"]
    def __str__(self): return self.nome
    def clean(self):
        from django.core.exceptions import ValidationError
        import re
        if self.cpf:
            digits=re.sub(r"\D","",self.cpf)
            if len(digits)!=11 or digits==digits[0]*11:
                raise ValidationError({"cpf":"Informe um CPF válido com 11 dígitos."})
            for pos in (9,10):
                total=sum(int(digits[i])*(pos+1-i) for i in range(pos))
                check=(total*10)%11
                if check==10: check=0
                if check!=int(digits[pos]):
                    raise ValidationError({"cpf":"O CPF informado não é válido."})
