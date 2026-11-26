import re

from django import forms

from .models import Fornecedor


class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = [
            "razao_social", "nome_fantasia", "cnpj", "inscricao_estadual", "contato",
            "telefone", "whatsapp", "email", "site", "endereco", "numero", "complemento",
            "bairro", "cidade", "estado", "cep", "observacoes", "ativo",
        ]
        widgets = {
            "observacoes": forms.Textarea(attrs={"rows": 3}),
        }
