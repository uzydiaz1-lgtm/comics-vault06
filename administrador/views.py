from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView

from comics.forms import ComicForm
from comics.models import Comic
from .models import ReporteBitacora


def index(request):
	return redirect('admin:index')


class StaffRequiredMixin(UserPassesTestMixin):
	raise_exception = True

	def test_func(self):
		return self.request.user.is_staff or self.request.user.is_superuser

	def handle_no_permission(self):
		if self.request.user.is_authenticated:
			return super().handle_no_permission()
		return redirect_to_login(
			self.request.get_full_path(),
			self.get_login_url(),
			self.get_redirect_field_name(),
		)


class ComicCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
	model = Comic
	form_class = ComicForm
	template_name = 'administrador/crear_comic.html'
	success_url = reverse_lazy('comics:catalogo')

	def form_valid(self, form):
		form.instance.propietario = self.request.user
		with transaction.atomic():
			response = super().form_valid(form)
			registrar_accion(self.request.user, 'Creación de cómic', self.object)
		messages.success(self.request, 'El cómic se creó correctamente.')
		return response


class ComicUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
	model = Comic
	form_class = ComicForm
	template_name = 'administrador/editar_comic.html'
	success_url = reverse_lazy('comics:catalogo')

	def form_valid(self, form):
		with transaction.atomic():
			response = super().form_valid(form)
			registrar_accion(self.request.user, 'Edición de cómic', self.object)
		messages.success(self.request, 'El cómic se actualizó correctamente.')
		return response


class ComicDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
	model = Comic
	template_name = 'administrador/comic_confirm_delete.html'
	success_url = reverse_lazy('comics:catalogo')

	def form_valid(self, form):
		comic = self.object
		with transaction.atomic():
			response = super().form_valid(form)
			registrar_accion(self.request.user, 'Eliminación de cómic', comic)
		messages.success(self.request, 'El cómic se eliminó correctamente.')
		return response


def registrar_accion(usuario, accion, comic):
	ReporteBitacora.objects.create(
		accion=accion,
		detalles=f'Cómic "{comic.titulo}" (ID: {comic.pk}).',
		nivel_severidad=1,
		usuario=usuario,
	)
