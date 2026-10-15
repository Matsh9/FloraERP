from django.urls import path
from . import views
urlpatterns=[path("alertas/",views.alertas,name="estoque_alertas"),path("movimentacoes/",views.movimentacoes,name="estoque_movimentacoes"),path("perdas/nova/",views.registrar_perda,name="estoque_perda")]
