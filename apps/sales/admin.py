from django.contrib import admin
from .models import Pedido,ItemPedido,Pagamento
admin.site.register(Pedido)
admin.site.register(ItemPedido)
admin.site.register(Pagamento)
