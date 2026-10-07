from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Q
from .models import Comic, CategoriaArea, UsuarioLector
from .forms import CategoriaAreaForm, ComicForm, PerfilLectorForm, UsuarioLectorForm

def inicio(request):
    return render(request, 'comics/inicio.html')

def catalogo_comics(request):
    query = request.GET.get('parametro', request.GET.get('q', '')).strip()
    categoria = request.GET.get('categoria', '').strip()

    comics = Comic.objects.select_related('categoria').all()
    categorias = CategoriaArea.objects.all()

    if query:
        comics = comics.filter(Q(titulo__icontains=query) | Q(autor__icontains=query))

    if categoria:
        comics = comics.filter(categoria__nombre__icontains=categoria)

    return render(request, 'comics/lista_comics.html', {
        'comics': comics,
        'query': query,
        'parametro': query,
        'categoria_seleccionada': categoria,
        'categorias': categorias,
    })


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

def detalle_comic(request, pk):
    comic = get_object_or_404(Comic, pk=pk)
    return render(request, 'comics/detalle_comic.html', {'comic': comic})

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
def crear_comic(request):
    if request.method == 'POST':
        form = ComicForm(request.POST, request.FILES)
        if form.is_valid():
            comic = form.save(commit=False)
            comic.propietario = request.user
            comic.save()
            messages.success(request, 'El cómic se creó correctamente.')
            return redirect('comics:catalogo')
    else:
        form = ComicForm()
    return render(request, 'comics/comic_form.html', {'form': form, 'accion': 'Nuevo'})

@login_required
def editar_comic(request, pk):
    comic = get_object_or_404(Comic, pk=pk)
    if comic.propietario != request.user:
        messages.error(request, 'No tienes permiso para realizar esta acción')
        return redirect('comics:catalogo')

    if request.method == 'POST':
        form = ComicForm(request.POST, request.FILES, instance=comic)
        if form.is_valid():
            form.save()
            messages.success(request, 'El cómic se actualizó correctamente.')
            return redirect('comics:detalle_comic', pk=comic.pk)
    else:
        form = ComicForm(instance=comic)
    return render(request, 'comics/comic_form.html', {'form': form, 'accion': 'Editar'})

@login_required
def eliminar_comic(request, pk):
    comic = get_object_or_404(Comic, pk=pk)
    if comic.propietario != request.user:
        messages.error(request, 'No tienes permiso para realizar esta acción')
        return redirect('comics:catalogo')

    if request.method == 'POST':
        comic.delete()
        messages.success(request, 'El cómic se eliminó correctamente.')
        return redirect('comics:catalogo')
    return render(request, 'comics/comic_confirm_delete.html', {'comic': comic})


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