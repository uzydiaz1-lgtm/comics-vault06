import logging
import smtplib
from functools import wraps

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from administrador.models import ReporteBitacora
from .forms import (
    CategoriaAreaForm,
    ContactoForm,
    LoginForm,
    PerfilLectorForm,
    RegistroForm,
    UsuarioLectorForm,
)
from .models import CategoriaArea, Comic, MensajeContacto, UsuarioLector


logger = logging.getLogger(__name__)


def staff_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapped_view


def inicio(request):
    return render(request, 'comics/inicio.html')


def contacto(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            contacto_obj = form.save()
            asunto = 'Nueva consulta web - Comic Vault'
            contexto = {
                'nombre': contacto_obj.nombre,
                'email': contacto_obj.email,
                'mensaje': contacto_obj.mensaje,
                'fecha': contacto_obj.fecha_envio,
                'asunto': asunto,
            }

            try:
                email_admin = EmailMessage(
                    subject=f'Nuevo mensaje de contacto de {contacto_obj.nombre}',
                    body=render_to_string('Autopartes/email-template.html', contexto),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.DEFAULT_FROM_EMAIL],
                    reply_to=[contacto_obj.email],
                )
                email_admin.content_subtype = 'html'
                admin_enviado = email_admin.send()
                respuesta_enviada = send_mail(
                    subject='Hemos recibido tu consulta - Comic Vault',
                    message=(
                        f'Hola {contacto_obj.nombre},\n\n'
                        'Gracias por comunicarte con nosotros. Hemos recibido tu '
                        'mensaje y te responderemos a la brevedad.\n\n'
                        'Atentamente,\nEl equipo de Comic Vault.'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[contacto_obj.email],
                )
                if not admin_enviado or not respuesta_enviada:
                    raise smtplib.SMTPException('El servidor no confirmó el envío de ambos correos.')
            except (OSError, smtplib.SMTPException, ValueError):
                logger.exception('No se pudieron enviar los correos del mensaje de contacto %s.', contacto_obj.pk)
                messages.warning(
                    request,
                    'Guardamos tu mensaje, pero no pudimos enviar la notificación por correo.',
                )
            else:
                messages.success(request, '¡Tu mensaje ha sido enviado con éxito!')
            return redirect('comics:gracias')
    else:
        form = ContactoForm()

    return render(request, 'Autopartes/contacto.html', {'form': form})


def pagina_de_gracias(request):
    return render(request, 'Autopartes/gracias.html')


def politica_privacidad(request):
    """Vista para renderizar la página de Política de Privacidad conforme Ley 25.326."""
    return render(request, 'Autopartes/politica_privacidad.html')


def terminos_condiciones(request):
    """Vista para renderizar la página de Términos y Condiciones."""
    return render(request, 'Autopartes/terminos_condiciones.html')


@staff_required
def listar_mensajes(request):
    mensajes_listado = MensajeContacto.objects.order_by('-fecha_envio')
    paginator = Paginator(mensajes_listado, 5)
    mensajes = paginator.get_page(request.GET.get('page'))
    return render(request, 'Autopartes/listar_mensajes.html', {'mensajes': mensajes})


class ComicListView(ListView):
    model = Comic
    template_name = 'comics/lista_comics.html'
    context_object_name = 'comics'

    def get_queryset(self):
        queryset = Comic.objects.select_related('categoria')
        self.query = (
            self.request.GET.get('q')
            or self.request.GET.get('parametro', '')
        ).strip()
        self.categoria = self.request.GET.get('categoria', '').strip()

        if self.query:
            queryset = queryset.filter(
                Q(titulo__icontains=self.query) | Q(autor__icontains=self.query)
            )
        if self.categoria:
            if self.categoria.isdecimal():
                queryset = queryset.filter(categoria_id=self.categoria)
            else:
                queryset = queryset.filter(categoria__nombre__icontains=self.categoria)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'query': self.query,
            'parametro': self.query,
            'categoria_seleccionada': self.categoria,
            'categorias': CategoriaArea.objects.order_by('nombre'),
        })
        return context


class ComicDetailView(DetailView):
    model = Comic
    template_name = 'comics/detalle_comic.html'
    context_object_name = 'comic'


def buscar_comics(request):
    return ComicListView.as_view()(request)


def registro_usuario(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                UsuarioLector.objects.create(user=user)
            login(request, user)
            messages.success(request, '¡Usuario registrado con éxito!')
            return redirect('comics:catalogo')
        messages.error(request, 'Por favor, corrige los errores indicados en el formulario.')
    else:
        form = RegistroForm()
    return render(request, 'comics/registro.html', {'form': form})


def login_lector(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'¡Bienvenido de nuevo, {user.username}!')
            return redirect('comics:catalogo')
        messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm(request)
    return render(request, 'comics/login_lector.html', {'form': form})


def login_admin(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff or user.is_superuser:
                login(request, user)
                messages.success(request, f'Sesión de administrador iniciada: {user.username}')
                return redirect('/admin/')
            messages.error(request, 'Acceso denegado. Esta cuenta no tiene permisos de administrador.')
        else:
            messages.error(request, 'Credenciales de administrador inválidas.')
    else:
        form = LoginForm(request)
    return render(request, 'comics/login_admin.html', {'form': form})


@require_POST
def logout_usuario(request):
    logout(request)
    return redirect('comics:catalogo')


@login_required
def perfil_usuario(request):
    perfil, _ = UsuarioLector.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = PerfilLectorForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu perfil se actualizó correctamente.')
            return redirect('comics:perfil')
    else:
        form = PerfilLectorForm(instance=perfil)

    return render(request, 'comics/perfil.html', {
        'form': form,
        'perfil': perfil,
    })


@staff_required
def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaAreaForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                categoria = form.save()
                ReporteBitacora.objects.create(
                    accion='Creación de categoría',
                    detalles=f'Categoría "{categoria.nombre}" (ID: {categoria.pk}).',
                    nivel_severidad=1,
                    usuario=request.user,
                )
            messages.success(request, 'La categoría se creó correctamente.')
            return redirect('comics:buscar_categorias')
    else:
        form = CategoriaAreaForm()
    return render(request, 'comics/categoria_form.html', {'form': form, 'accion': 'Nueva'})


def buscar_categorias(request):
    parametro = request.GET.get('parametro', '').strip()
    categorias = CategoriaArea.objects.all()
    if parametro:
        categorias = categorias.filter(
            Q(nombre__icontains=parametro) | Q(descripcion__icontains=parametro)
        )
    return render(request, 'comics/lista_categorias.html', {
        'categorias': categorias,
        'resultados': categorias,
        'parametro': parametro,
    })


@staff_required
def buscar_usuarios(request):
    parametro = request.GET.get('parametro', '').strip()
    usuarios = UsuarioLector.objects.select_related('user').all()
    if parametro:
        usuarios = usuarios.filter(
            Q(alias__icontains=parametro)
            | Q(user__username__icontains=parametro)
            | Q(user__email__icontains=parametro)
        )
    return render(request, 'comics/lista_usuarios.html', {
        'usuarios': usuarios,
        'resultados': usuarios,
        'parametro': parametro,
    })


@staff_required
def crear_usuario_lector(request):
    if request.method == 'POST':
        form = UsuarioLectorForm(request.POST)
        if form.is_valid():
            perfil = form.save()
            ReporteBitacora.objects.create(
                accion='Creación de perfil lector',
                detalles=f'Perfil lector para "{perfil.user.username}" (ID: {perfil.pk}).',
                nivel_severidad=1,
                usuario=request.user,
            )
            messages.success(request, 'El perfil de lector se creó correctamente.')
            return redirect('comics:buscar_usuarios')
    else:
        form = UsuarioLectorForm()
    return render(request, 'comics/usuario_form.html', {'form': form, 'accion': 'Nuevo'})
