from django.contrib import admin
# CRÍTICO: Asegúrate de importar 'include' además de 'path'
from django.urls import path, include 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('comics.urls')),
    path('gestion/', include('administrador.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)