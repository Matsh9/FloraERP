from django import forms
from .models import Produto, Categoria, FichaBotanica
class ProdutoForm(forms.ModelForm):
    class Meta:
        model=Produto
        fields=["nome","sku","categoria","descricao","imagem","preco_venda","custo_aquisicao","estoque","estoque_minimo","unidade","ativo"]
        widgets={"descricao":forms.Textarea(attrs={"rows":3})}
class CategoriaForm(forms.ModelForm):
    class Meta: model=Categoria; fields=["nome","slug","descricao","ativa"]
class FichaBotanicaForm(forms.ModelForm):
    class Meta:
        model=FichaBotanica
        fields=["nome_cientifico","iluminacao","rega","temperatura","cuidados_especiais","beneficios_usos","argumentos_venda","complementares"]
