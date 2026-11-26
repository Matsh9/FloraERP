from django.urls import path

from . import views


urlpatterns = [
    path("", views.lista, name="fornecedores_lista"),
    path("novo/", views.criar, name="fornecedor_criar"),
    path("<int:pk>/", views.detalhe, name="fornecedor_detalhe"),
    path("<int:pk>/editar/", views.editar, name="fornecedor_editar"),
]
