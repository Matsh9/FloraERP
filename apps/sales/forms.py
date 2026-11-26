from django import forms

from apps.customers.models import Cliente
from .models import Pedido


class VendaForm(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.filter(ativo=True), required=False)
    forma_pagamento = forms.ChoiceField(choices=Pedido.PAGAMENTOS[:-1])
    desconto = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0, initial=0)
    produto = forms.CharField(max_length=40, help_text="SKU do produto para adicionar ao carrinho")
    quantidade = forms.DecimalField(max_digits=8, decimal_places=2, min_value=0.01, initial=1)


class PedidoPersonalizadoForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.filter(ativo=True),
        required=True,
        label="Cliente",
    )

    class Meta:
        model = Pedido
        fields = ["cliente", "observacoes"]
        labels = {"observacoes": "Observações e detalhes do pedido"}
        widgets = {
            "observacoes": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Ex.: cores, tamanho, entrega, mensagem no cartão ou embalagem",
                }
            ),
        }
