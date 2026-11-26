from django.contrib import admin
from .models import PerdaEstoque, MovimentacaoEstoque, Lote


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ("produto", "codigo", "quantidade_inicial", "quantidade_disponivel", "data_entrada", "data_validade", "legado")
    list_filter = ("data_validade", "legado")
    search_fields = ("produto__nome", "produto__sku", "codigo")
    readonly_fields = tuple(field.name for field in Lote._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = ("criado_em", "produto", "lote", "tipo", "quantidade", "usuario")
    list_filter = ("tipo", "criado_em")
    search_fields = ("produto__nome", "produto__sku", "lote__codigo", "referencia")
    readonly_fields = tuple(field.name for field in MovimentacaoEstoque._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PerdaEstoque)
class PerdaEstoqueAdmin(admin.ModelAdmin):
    list_display = ("produto", "quantidade", "motivo", "criado_em", "usuario")
    readonly_fields = tuple(field.name for field in PerdaEstoque._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
