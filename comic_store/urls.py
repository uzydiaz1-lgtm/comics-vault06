from django.contrib import admin
# CRÍTICO: Asegúrate de importar 'include' además de 'path'
from django.urls import path, include 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Aquí le decimos a Django: "Cualquier petición a la raíz (''), 
    # envíala al archivo urls.py de la aplicación 'comics'"
    path('', include('comics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)