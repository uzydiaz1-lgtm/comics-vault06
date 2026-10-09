from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.urls import reverse
from .models import CategoriaArea, Comic


class LoginViewsTests(TestCase):
	def setUp(self):
		self.password = 'test-password-123'
		self.lector = User.objects.create_user(username='lector', password=self.password)
		self.admin = User.objects.create_user(
			username='admin',
			password=self.password,
			is_staff=True,
		)

	def test_lector_login_redirects_to_catalog(self):
		response = self.client.post(reverse('comics:login'), {
			'username': self.lector.username,
			'password': self.password,
		})

		self.assertRedirects(response, reverse('comics:catalogo'))

	def test_admin_login_rejects_lector(self):
		response = self.client.post(reverse('comics:login_admin'), {
			'username': self.lector.username,
			'password': self.password,
		})

		self.assertEqual(response.status_code, 200)
		self.assertNotIn('_auth_user_id', self.client.session)

	def test_admin_login_redirects_staff_to_admin(self):
		response = self.client.post(reverse('comics:login_admin'), {
			'username': self.admin.username,
			'password': self.password,
		})

		self.assertRedirects(response, '/admin/', fetch_redirect_response=False)


class ComicOwnershipTests(TestCase):
	def setUp(self):
		self.owner = User.objects.create_user(username='owner', password='test-password-123')
		self.other_user = User.objects.create_user(username='other', password='test-password-123')
		self.category = CategoriaArea.objects.create(nombre='Manga')
		self.comic = Comic.objects.create(
			titulo='Comic de prueba',
			autor='Editorial de prueba',
			categoria=self.category,
			propietario=self.owner,
		)

	def test_non_owner_cannot_edit_or_delete_comic(self):
		self.client.force_login(self.other_user)

		for route_name in ('administrador:editar_comic', 'administrador:eliminar_comic'):
			response = self.client.get(reverse(route_name, args=[self.comic.pk]))

			self.assertRedirects(response, reverse('comics:catalogo'))
			self.assertEqual(
				list(get_messages(response.wsgi_request))[0].message,
				'No tienes permiso para modificar este cómic.',
			)

		self.assertTrue(Comic.objects.filter(pk=self.comic.pk).exists())

	def test_anonymous_user_is_redirected_to_login_for_edit_and_delete(self):
		for route_name in ('administrador:editar_comic', 'administrador:eliminar_comic'):
			response = self.client.get(reverse(route_name, args=[self.comic.pk]))

			self.assertRedirects(
				response,
				reverse('comics:login') + '?next=' + reverse(route_name, args=[self.comic.pk]),
			)

	def test_comic_creation_assigns_authenticated_user_as_owner(self):
		self.client.force_login(self.owner)

		response = self.client.post(reverse('administrador:crear_comic'), {
			'titulo': 'Nuevo cómic',
			'autor': 'Editorial nueva',
			'anio': 2025,
			'sinopsis': 'Sinopsis de prueba',
			'categoria': self.category.pk,
		})

		self.assertRedirects(response, reverse('comics:catalogo'))
		created_comic = Comic.objects.get(titulo='Nuevo cómic')
		self.assertEqual(created_comic.propietario, self.owner)

	def test_catalog_shows_actions_only_to_comic_owner(self):
		edit_url = reverse('administrador:editar_comic', args=[self.comic.pk])
		delete_url = reverse('administrador:eliminar_comic', args=[self.comic.pk])

		self.client.force_login(self.owner)
		owner_response = self.client.get(reverse('comics:catalogo'))
		self.assertContains(owner_response, edit_url)
		self.assertContains(owner_response, delete_url)

		self.client.force_login(self.other_user)
		other_response = self.client.get(reverse('comics:catalogo'))
		self.assertNotContains(other_response, edit_url)
		self.assertNotContains(other_response, delete_url)
