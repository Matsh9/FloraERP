from django.urls import path
from . import views
urlpatterns=[path("",views.lista,name="catalogo_lista"),path("novo/",views.criar,name="produto_criar"),path("<int:pk>/",views.detalhe,name="produto_detalhe"),path("<int:pk>/editar/",views.editar,name="produto_editar"),path("<int:pk>/arquivar/",views.arquivar,name="produto_arquivar")]
