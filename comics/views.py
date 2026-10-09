from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Q
from django.views.generic import ListView, DetailView
from .models import Comic, CategoriaArea, UsuarioLector
from .forms import CategoriaAreaForm, PerfilLectorForm, UsuarioLectorForm

def inicio(request):
    return render(request, 'comics/inicio.html')

class ComicListView(ListView):
    model = Comic
    template_name = 'comics/lista_comics.html'
    context_object_name = 'comics'

    def get_queryset(self):
        queryset = Comic.objects.select_related('categoria')
        self.query = self.request.GET.get('q') or self.request.GET.get('parametro', '')
        self.query = self.query.strip()
        self.categoria = self.request.GET.get('categoria', '').strip()

        if self.query:
            queryset = queryset.filter(
                Q(titulo__icontains=self.query) | Q(autor__icontains=self.query)
            )
        if self.categoria:
            queryset = queryset.filter(categoria__nombre__icontains=self.categoria)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'query': self.query,
            'parametro': self.query,
            'categoria_seleccionada': self.categoria,
            'categorias': CategoriaArea.objects.all(),
        })
        return context


class ComicDetailView(DetailView):
    model = Comic
    template_name = 'comics/detalle_comic.html'
    context_object_name = 'comic'


def buscar_comics(request):
    parametro = request.GET.get('parametro', '').strip()
    comics = Comic.objects.select_related('categoria').all()
    if parametro:
        comics = comics.filter(
            Q(titulo__icontains=parametro)
            | Q(autor__icontains=parametro)
            | Q(categoria__nombre__icontains=parametro)
        )
    return render(request, 'comics/lista_comics.html', {
        'comics': comics,
        'resultados': comics,
        'parametro': parametro,
        'query': parametro,
        'categorias': CategoriaArea.objects.all(),
    })

def registro_usuario(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UsuarioLector.objects.create(user=user)
            login(request, user)
            messages.success(request, '¡Usuario registrado con éxito!')
            return redirect('comics:catalogo')
        messages.error(request, 'Por favor, corrige los errores indicados en el formulario.')
    else:
        form = UserCreationForm()
    return render(request, 'comics/registro.html', {'form': form})

def login_lector(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'¡Bienvenido de nuevo, {user.username}!')
            return redirect('comics:catalogo')
        messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = AuthenticationForm()
    return render(request, 'comics/login_lector.html', {'form': form})

def login_admin(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
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
        form = AuthenticationForm()
    return render(request, 'comics/login_admin.html', {'form': form})

def logout_usuario(request):
    logout(request)
    return redirect('comics:catalogo')

@login_required
def perfil_usuario(request):
    perfil, created = UsuarioLector.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = PerfilLectorForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('comics:perfil')
    else:
        form = PerfilLectorForm(instance=perfil)

    return render(request, 'comics/perfil.html', {
        'form': form,
        'perfil': perfil,
    })

@login_required
def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaAreaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'El área se creó correctamente.')
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


@login_required
def crear_usuario_lector(request):
    if request.method == 'POST':
        form = UsuarioLectorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'El perfil de lector se creó correctamente.')
            return redirect('comics:buscar_usuarios')
    else:
        form = UsuarioLectorForm()
    return render(request, 'comics/usuario_form.html', {'form': form, 'accion': 'Nuevo'})