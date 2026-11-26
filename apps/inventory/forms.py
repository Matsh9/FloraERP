from decimal import Decimal
from django import forms
from .models import PerdaEstoque, Lote
from apps.catalog.models import Produto


class EntradaLoteForm(forms.ModelForm):
    data_validade = forms.DateField(label="Data de validade", required=True, widget=forms.DateInput(attrs={"type":"date"}))

    class Meta:
        model = Lote
        fields = ["produto", "codigo", "quantidade_inicial", "data_entrada", "data_validade", "custo_unitario", "observacao"]
        labels = {"produto":"Produto","codigo":"Código do lote","quantidade_inicial":"Quantidade","data_entrada":"Data de entrada","data_validade":"Data de validade","custo_unitario":"Custo unitário (R$)","observacao":"Observação"}
        widgets = {"data_entrada":forms.DateInput(attrs={"type":"date"}),"data_validade":forms.DateInput(attrs={"type":"date"}),"observacao":forms.Textarea(attrs={"rows":3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["produto"].queryset = Produto.objects.filter(ativo=True).order_by("nome")
        self.fields["quantidade_inicial"].min_value = Decimal("0.01")
        self.fields["custo_unitario"].min_value = Decimal("0")


class PerdaForm(forms.ModelForm):
    custo_estimado = forms.DecimalField(label="Custo estimado (R$)", min_value=0, max_digits=10, decimal_places=2, required=False,
        widget=forms.NumberInput(attrs={"readonly": True, "step": "0.01", "placeholder": "R$ 0,00"}))
    class Meta:
        model=PerdaEstoque
        fields=["produto","quantidade","motivo","observacao","custo_estimado"]
        widgets={"observacao":forms.Textarea(attrs={"rows":3})}
    def clean(self):
        cleaned_data=super().clean()
        produto=cleaned_data.get("produto"); quantidade=cleaned_data.get("quantidade")
        if produto and quantidade and quantidade>0:
            preco=produto.preco_venda or produto.custo_aquisicao or Decimal("0")
            cleaned_data["custo_estimado"]=preco*Decimal(str(quantidade))
        return cleaned_data
