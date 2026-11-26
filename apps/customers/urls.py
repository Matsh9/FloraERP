from django.urls import path
from . import views
urlpatterns=[path("",views.lista,name="clientes_lista"),path("novo/",views.criar,name="cliente_criar"),path("<int:pk>/",views.detalhe,name="cliente_detalhe"),path("<int:pk>/editar/",views.editar,name="cliente_editar")]
