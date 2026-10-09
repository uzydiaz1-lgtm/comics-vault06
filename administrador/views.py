from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView

from comics.models import Comic


class ComicCreateView(LoginRequiredMixin, CreateView):
	model = Comic
	template_name = 'administrador/crear_comic.html'
	fields = ['titulo', 'autor', 'anio', 'sinopsis', 'categoria', 'portada']
	success_url = reverse_lazy('comics:catalogo')

	def form_valid(self, form):
		form.instance.propietario = self.request.user
		messages.success(self.request, 'El cómic se creó correctamente.')
		return super().form_valid(form)


class ComicUpdateView(LoginRequiredMixin, UpdateView):
	model = Comic
	template_name = 'administrador/editar_comic.html'
	fields = ['titulo', 'autor', 'anio', 'sinopsis', 'categoria', 'portada']
	success_url = reverse_lazy('comics:catalogo')

	def dispatch(self, request, *args, **kwargs):
		if not request.user.is_authenticated:
			return self.handle_no_permission()
		if self.get_object().propietario != request.user:
			messages.error(request, 'No tienes permiso para modificar este cómic.')
			return redirect('comics:catalogo')
		return super().dispatch(request, *args, **kwargs)

	def form_valid(self, form):
		messages.success(self.request, 'El cómic se actualizó correctamente.')
		return super().form_valid(form)


class ComicDeleteView(LoginRequiredMixin, DeleteView):
	model = Comic
	template_name = 'administrador/comic_confirm_delete.html'
	success_url = reverse_lazy('comics:catalogo')

	def dispatch(self, request, *args, **kwargs):
		if not request.user.is_authenticated:
			return self.handle_no_permission()
		if self.get_object().propietario != request.user:
			messages.error(request, 'No tienes permiso para modificar este cómic.')
			return redirect('comics:catalogo')
		return super().dispatch(request, *args, **kwargs)

	def form_valid(self, form):
		messages.success(self.request, 'El cómic se eliminó correctamente.')
		return super().form_valid(form)
