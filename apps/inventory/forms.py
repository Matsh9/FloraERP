from django import forms
from .models import PerdaEstoque
class PerdaForm(forms.ModelForm):
    class Meta:
        model=PerdaEstoque
        fields=["produto","quantidade","motivo","observacao","custo_estimado"]
        widgets={"observacao":forms.Textarea(attrs={"rows":3})}
