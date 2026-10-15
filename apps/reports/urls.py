from django.urls import path
from . import views
urlpatterns=[path("",views.index,name="relatorios_index"),path("vendas.csv",views.exportar_vendas,name="relatorios_exportar")]
