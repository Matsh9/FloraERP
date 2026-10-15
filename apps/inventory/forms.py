from decimal import Decimal
from django import forms
from .models import PerdaEstoque

class PerdaForm(forms.ModelForm):
    custo_estimado = forms.DecimalField(
        label="Custo estimado (R$)",
        min_value=0,
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={"readonly": True, "step": "0.01", "placeholder": "R$ 0,00"}),
    )

    class Meta:
        model=PerdaEstoque
        fields=["produto","quantidade","motivo","observacao","custo_estimado"]
        widgets={"observacao":forms.Textarea(attrs={"rows":3})}

    def clean(self):
        cleaned_data = super().clean()
        produto = cleaned_data.get("produto")
        quantidade = cleaned_data.get("quantidade")
        if produto and quantidade and quantidade > 0:
            preco_unitario = produto.preco_venda or produto.custo_aquisicao or Decimal("0")
            cleaned_data["custo_estimado"] = preco_unitario * Decimal(str(quantidade))
        return cleaned_data
