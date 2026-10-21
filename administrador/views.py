from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView

from .forms import ComicAdminForm
from comics.models import Comic


def index(request):
	return redirect('admin:index')


class StaffRequiredMixin(UserPassesTestMixin):
	raise_exception = True

	def test_func(self):
		return self.request.user.is_staff

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
	form_class = ComicAdminForm
	template_name = 'administrador/crear_comic.html'
	success_url = reverse_lazy('comics:catalogo')

	def form_valid(self, form):
		form.instance.propietario = self.request.user
		messages.success(self.request, 'El cómic se creó correctamente.')
		return super().form_valid(form)


class ComicUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
	model = Comic
	form_class = ComicAdminForm
	template_name = 'administrador/editar_comic.html'
	success_url = reverse_lazy('comics:catalogo')

	def form_valid(self, form):
		messages.success(self.request, 'El cómic se actualizó correctamente.')
		return super().form_valid(form)


class ComicDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
	model = Comic
	template_name = 'administrador/comic_confirm_delete.html'
	success_url = reverse_lazy('comics:catalogo')

	def form_valid(self, form):
		messages.success(self.request, 'El cómic se eliminó correctamente.')
		return super().form_valid(form)
