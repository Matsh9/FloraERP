from django import forms
from .models import Entrega
class EntregaForm(forms.ModelForm):
    class Meta:
        model=Entrega
        fields=["pedido","cliente","telefone","cpf","endereco","numero","complemento","bairro","cidade","estado","cep","data_entrega","horario_entrega","observacoes","responsavel","status"]
        widgets={"data_entrega":forms.DateInput(attrs={"type":"date"}),"horario_entrega":forms.TimeInput(attrs={"type":"time"}),"observacoes":forms.Textarea(attrs={"rows":3})}
