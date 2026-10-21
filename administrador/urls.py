from django.urls import path
from . import views

app_name = 'administrador'

urlpatterns = [
    path('', views.index, name='index'),
    path('nuevo/', views.ComicCreateView.as_view(), name='crear_comic'),
    path('editar/<int:pk>/', views.ComicUpdateView.as_view(), name='editar_comic'),
    path('eliminar/<int:pk>/', views.ComicDeleteView.as_view(), name='eliminar_comic'),
]