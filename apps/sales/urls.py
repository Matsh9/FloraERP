from django.urls import path
from . import views
urlpatterns=[path("pdv/",views.pdv,name="vendas_pdv"),path("",views.historico,name="vendas_historico"),path("<int:pk>/",views.detalhe,name="venda_detalhe"),path("<int:pk>/comprovante/",views.comprovante,name="venda_comprovante"),path("<int:pk>/cancelar/",views.cancelar,name="venda_cancelar")]
