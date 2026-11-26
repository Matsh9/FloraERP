from django.contrib import admin
from .models import Categoria, Produto, FichaBotanica, Kit, ItemKit

admin.site.register(Categoria)

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    readonly_fields = ("estoque", "data_validade", "criado_em", "atualizado_em")
    list_display = ("nome", "sku", "estoque", "estoque_minimo", "ativo")
    search_fields = ("nome", "sku")

admin.site.register(FichaBotanica)
admin.site.register(Kit)
admin.site.register(ItemKit)
