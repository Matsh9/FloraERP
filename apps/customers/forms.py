from django import forms
from .models import Cliente
class ClienteForm(forms.ModelForm):
    class Meta:
        model=Cliente
        fields=["nome","cpf","telefone","whatsapp","email","data_nascimento","endereco","numero","complemento","bairro","cidade","estado","cep","preferencias","observacoes","ativo"]
        widgets={"data_nascimento":forms.DateInput(attrs={"type":"date"}),"preferencias":forms.Textarea(attrs={"rows":2}),"observacoes":forms.Textarea(attrs={"rows":2})}
    def clean_cpf(self):
        cpf=self.cleaned_data.get("cpf","").strip()
        if cpf: self.instance.cpf=cpf; self.instance.clean()
        return cpf
