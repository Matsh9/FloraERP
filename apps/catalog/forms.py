from django import forms
from .models import Produto, Categoria, FichaBotanica

class ProdutoForm(forms.ModelForm):
    preco_venda = forms.DecimalField(
        label="Preço de venda (R$)",
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"step": "0.01", "min": "0", "placeholder": "0,00"}),
    )
    custo_aquisicao = forms.DecimalField(
        label="Custo de aquisição (R$)",
        min_value=0,
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={"step": "0.01", "min": "0", "placeholder": "0,00"}),
    )
    estoque = forms.IntegerField(
        label="Estoque",
        min_value=0,
        widget=forms.NumberInput(attrs={"step": "1", "min": "0", "placeholder": "0"}),
    )
    estoque_minimo = forms.IntegerField(
        label="Estoque mínimo",
        min_value=0,
        widget=forms.NumberInput(attrs={"step": "1", "min": "0", "placeholder": "0"}),
    )

    class Meta:
        model=Produto
        fields=["nome","sku","categoria","descricao","imagem","preco_venda","custo_aquisicao","estoque","estoque_minimo","unidade","ativo"]
        labels={
            "nome": "Nome",
            "sku": 'SKU ("Código único do produto")',
            "categoria": "Categoria",
            "descricao": "Descrição",
            "imagem": "Imagem",
            "unidade": "Unidade",
            "ativo": "Ativo",
        }
        widgets={"descricao":forms.Textarea(attrs={"rows":3}), "sku":forms.TextInput(attrs={"placeholder":"EX: ROS-001"})}
class CategoriaForm(forms.ModelForm):
    class Meta: model=Categoria; fields=["nome","slug","descricao","ativa"]
class FichaBotanicaForm(forms.ModelForm):
    class Meta:
        model=FichaBotanica
        fields=["nome_cientifico","iluminacao","rega","temperatura","cuidados_especiais","beneficios_usos","argumentos_venda","complementares"]
