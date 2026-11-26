from django import forms
from apps.customers.models import Cliente
from .models import Pedido
class VendaForm(forms.Form):
    cliente=forms.ModelChoiceField(queryset=Cliente.objects.filter(ativo=True),required=False)
    forma_pagamento=forms.ChoiceField(choices=Pedido.PAGAMENTOS[:-1])
    desconto=forms.DecimalField(max_digits=10,decimal_places=2,min_value=0,initial=0)
    produto=forms.CharField(max_length=40,help_text="SKU do produto para adicionar ao carrinho")
    quantidade=forms.DecimalField(max_digits=8,decimal_places=2,min_value=0.01,initial=1)
