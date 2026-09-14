from django.urls import path
from . import views

app_name = 'comics'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('catalogo/', views.catalogo_comics, name='catalogo'),
    path('buscar/comics/', views.buscar_comics, name='buscar_comics'),
    path('buscar/categorias/', views.buscar_categorias, name='buscar_categorias'),
    path('buscar/usuarios/', views.buscar_usuarios, name='buscar_usuarios'),
    path('comic/<int:pk>/', views.detalle_comic, name='detalle_comic'),
    path('registro/', views.registro_usuario, name='registro'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('nuevo/', views.crear_comic, name='crear_comic'),
    path('nueva-categoria/', views.crear_categoria, name='crear_categoria'),
    path('nuevo-lector/', views.crear_usuario_lector, name='crear_usuario_lector'),
    path('editar/<int:pk>/', views.editar_comic, name='editar_comic'),
    path('eliminar/<int:pk>/', views.eliminar_comic, name='eliminar_comic'),
]