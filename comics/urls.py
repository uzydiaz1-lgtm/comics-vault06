from django.urls import path
from . import views

app_name = 'comics'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('contacto/', views.contacto, name='contacto'),
    path('gracias/', views.pagina_de_gracias, name='gracias'),
    path('politica-privacidad/', views.politica_privacidad, name='politica_privacidad'),
    path('terminos-condiciones/', views.terminos_condiciones, name='terminos_condiciones'),
    path('listar-mensajes/', views.listar_mensajes, name='listar_mensajes'),
    path('catalogo/', views.ComicListView.as_view(), name='catalogo'),
    path('buscar/comics/', views.buscar_comics, name='buscar_comics'),
    path('buscar/categorias/', views.buscar_categorias, name='buscar_categorias'),
    path('buscar/usuarios/', views.buscar_usuarios, name='buscar_usuarios'),
    path('detalle/<int:pk>/', views.ComicDetailView.as_view(), name='detalle_comic'),
    path('registro/', views.registro_usuario, name='registro'),
    path('login/', views.login_lector, name='login'),
    path('login/admin/', views.login_admin, name='login_admin'),
    path('logout/', views.logout_usuario, name='logout'),
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('nueva-categoria/', views.crear_categoria, name='crear_categoria'),
    path('nuevo-lector/', views.crear_usuario_lector, name='crear_usuario_lector'),
]