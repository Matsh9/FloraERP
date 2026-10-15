from django.urls import path
from . import views
urlpatterns=[path("",views.lista,name="entregas_lista"),path("nova/",views.criar,name="entrega_criar"),path("<int:pk>/editar/",views.editar,name="entrega_editar")]
