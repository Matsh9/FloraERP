from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core import views as core_views
urlpatterns = [
 path("admin/",admin.site.urls),
 path("accounts/",include("django.contrib.auth.urls")),
 path("",include("apps.core.urls")),
 path("catalogo/",include("apps.catalog.urls")),
 path("clientes/",include("apps.customers.urls")),
 path("estoque/",include("apps.inventory.urls")),
 path("vendas/",include("apps.sales.urls")),
 path("entregas/",include("apps.deliveries.urls")),
 path("relatorios/",include("apps.reports.urls")),
]
if settings.DEBUG:
 urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
