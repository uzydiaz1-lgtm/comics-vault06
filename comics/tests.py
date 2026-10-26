from io import BytesIO
from tempfile import TemporaryDirectory

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings
from django.urls import reverse
from PIL import Image

from administrador.models import ReporteBitacora
from .models import CategoriaArea, Comic


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
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

	def test_logout_requires_post_and_clears_session(self):
		self.client.force_login(self.lector)

		get_response = self.client.get(reverse('comics:logout'))
		self.assertEqual(get_response.status_code, 405)
		self.assertIn('_auth_user_id', self.client.session)

		post_response = self.client.post(reverse('comics:logout'))
		self.assertRedirects(post_response, reverse('comics:catalogo'))
		self.assertNotIn('_auth_user_id', self.client.session)


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class ComicOwnershipTests(TestCase):
	def setUp(self):
		self.owner = User.objects.create_user(
			username='owner',
			password='test-password-123',
			is_staff=True,
		)
		self.other_user = User.objects.create_user(username='other', password='test-password-123')
		self.category = CategoriaArea.objects.create(nombre='Manga')
		self.comic = Comic.objects.create(
			titulo='Comic de prueba',
			autor='Editorial de prueba',
			categoria=self.category,
			propietario=self.owner,
		)

	def test_non_staff_cannot_edit_or_delete_comic(self):
		self.client.force_login(self.other_user)

		for route_name in ('administrador:editar_comic', 'administrador:eliminar_comic'):
			response = self.client.get(reverse(route_name, args=[self.comic.pk]))

			self.assertEqual(response.status_code, 403)

		self.assertTrue(Comic.objects.filter(pk=self.comic.pk).exists())

	def test_non_staff_cannot_create_comic(self):
		self.client.force_login(self.other_user)

		response = self.client.get(reverse('administrador:crear_comic'))

		self.assertEqual(response.status_code, 403)

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


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class CatalogSearchTests(TestCase):
	def setUp(self):
		self.manga = CategoriaArea.objects.create(nombre='Manga')
		self.indie = CategoriaArea.objects.create(nombre='Independiente')
		Comic.objects.create(titulo='La ciudad', autor='A. Rivera', categoria=self.manga)
		Comic.objects.create(titulo='Otro título', autor='A. Rivera', categoria=self.indie)
		Comic.objects.create(titulo='La ciudad', autor='Otra autora', categoria=self.indie)

	def test_search_matches_title_or_author_and_combines_category(self):
		response = self.client.get(reverse('comics:catalogo'), {
			'parametro': 'A. Rivera',
			'categoria': self.manga.pk,
		})

		self.assertEqual(response.status_code, 200)
		self.assertEqual([comic.titulo for comic in response.context['comics']], ['La ciudad'])

	def test_search_by_title_and_category_name(self):
		response = self.client.get(reverse('comics:buscar_comics'), {
			'q': 'La ciudad',
			'categoria': 'Independiente',
		})

		self.assertEqual(response.status_code, 200)
		self.assertEqual([comic.autor for comic in response.context['comics']], ['Otra autora'])

	def test_empty_search_shows_no_results_message(self):
		response = self.client.get(reverse('comics:catalogo'), {'parametro': 'No existe'})

		self.assertContains(response, 'No encontramos cómics que coincidan con tus filtros.')


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class ProfileAndRegistrationTests(TestCase):
	def test_registration_creates_reader_profile_and_hashed_password(self):
		response = self.client.post(reverse('comics:registro'), {
			'username': 'nuevo-lector',
			'password1': 'different-password-42',
			'password2': 'different-password-42',
		})

		self.assertRedirects(response, reverse('comics:catalogo'))
		user = User.objects.get(username='nuevo-lector')
		self.assertTrue(user.check_password('different-password-42'))
		self.assertNotEqual(user.password, 'different-password-42')
		self.assertTrue(hasattr(user, 'perfil'))

	def test_reader_can_update_contact_information(self):
		user = User.objects.create_user(username='lector', password='test-password-123')
		self.client.force_login(user)

		response = self.client.post(reverse('comics:perfil'), {
			'alias': 'Lectora',
			'telefono': '+56 9 1234 5678',
			'direccion': 'Calle de prueba 123',
			'ciudad': 'Santiago',
			'comic_favorito': '',
		})

		self.assertRedirects(response, reverse('comics:perfil'))
		user.perfil.refresh_from_db()
		self.assertEqual(user.perfil.telefono, '+56 9 1234 5678')
		self.assertEqual(user.perfil.direccion, 'Calle de prueba 123')
		self.assertEqual(user.perfil.ciudad, 'Santiago')


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class AdministrativeAccessAndAuditTests(TestCase):
	def setUp(self):
		self.staff = User.objects.create_user(
			username='staff',
			password='staff-password-123',
			is_staff=True,
		)
		self.reader = User.objects.create_user(username='reader', password='reader-password-123')
		self.category = CategoriaArea.objects.create(nombre='Manga')
		self.comic = Comic.objects.create(
			titulo='Original',
			autor='Autora',
			categoria=self.category,
		)

	def test_non_staff_cannot_manage_categories_or_reader_profiles(self):
		self.client.force_login(self.reader)

		for route_name in (
			'comics:crear_categoria',
			'comics:buscar_usuarios',
			'comics:crear_usuario_lector',
		):
			with self.subTest(route=route_name):
				self.assertEqual(self.client.get(reverse(route_name)).status_code, 403)

	def test_staff_can_create_category_and_reader_profile_with_audit_entries(self):
		self.client.force_login(self.staff)
		response = self.client.post(reverse('comics:crear_categoria'), {
			'nombre': 'Webtoon',
			'descripcion': 'Historietas digitales',
		})

		self.assertRedirects(response, reverse('comics:buscar_categorias'))
		self.assertTrue(ReporteBitacora.objects.filter(
			accion='Creación de categoría',
			usuario=self.staff,
		).exists())

		response = self.client.post(reverse('comics:crear_usuario_lector'), {
			'user': self.reader.pk,
			'alias': 'Fan',
			'telefono': '123456',
			'direccion': 'Dirección',
			'ciudad': 'Ciudad',
			'comic_favorito': '',
		})
		self.assertRedirects(response, reverse('comics:buscar_usuarios'))
		self.assertEqual(self.reader.perfil.alias, 'Fan')
		self.assertTrue(ReporteBitacora.objects.filter(
			accion='Creación de perfil lector',
			usuario=self.staff,
		).exists())

	def test_staff_can_create_edit_and_post_delete_comics_with_audit(self):
		self.client.force_login(self.staff)

		response = self.client.post(reverse('administrador:crear_comic'), {
			'titulo': 'Nuevo',
			'autor': 'Autor nuevo',
			'anio': 2025,
			'sinopsis': 'Resumen',
			'categoria': self.category.pk,
		})
		self.assertRedirects(response, reverse('comics:catalogo'))
		created = Comic.objects.get(titulo='Nuevo')

		response = self.client.post(reverse('administrador:editar_comic', args=[created.pk]), {
			'titulo': 'Actualizado',
			'autor': 'Autor actualizado',
			'anio': 2026,
			'sinopsis': 'Resumen editado',
			'categoria': self.category.pk,
		})
		self.assertRedirects(response, reverse('comics:catalogo'))
		created.refresh_from_db()
		self.assertEqual(created.titulo, 'Actualizado')

		delete_url = reverse('administrador:eliminar_comic', args=[created.pk])
		confirmation = self.client.get(delete_url)
		self.assertEqual(confirmation.status_code, 200)
		self.assertTrue(Comic.objects.filter(pk=created.pk).exists())
		self.assertEqual(self.client.post(delete_url).status_code, 302)
		self.assertFalse(Comic.objects.filter(pk=created.pk).exists())
		self.assertEqual(
			ReporteBitacora.objects.filter(usuario=self.staff).count(),
			3,
		)

	def test_delete_requires_csrf_token(self):
		client = Client(enforce_csrf_checks=True)
		client.force_login(self.staff)
		delete_url = reverse('administrador:eliminar_comic', args=[self.comic.pk])

		self.assertEqual(client.get(delete_url).status_code, 200)
		self.assertEqual(client.post(delete_url).status_code, 403)
		self.assertTrue(Comic.objects.filter(pk=self.comic.pk).exists())


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class ComicCoverUploadTests(TestCase):
	def test_admin_uploads_and_displays_comic_cover(self):
		staff = User.objects.create_user(
			username='staff',
			password='staff-password-123',
			is_staff=True,
		)
		category = CategoriaArea.objects.create(nombre='Manga')
		image_buffer = BytesIO()
		Image.new('RGB', (2, 2), color='red').save(image_buffer, format='PNG')
		uploaded_image = SimpleUploadedFile(
			'portada.png',
			image_buffer.getvalue(),
			content_type='image/png',
		)
		self.client.force_login(staff)

		with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
			response = self.client.post(reverse('administrador:crear_comic'), {
				'titulo': 'Con portada',
				'autor': 'Autora',
				'anio': 2025,
				'sinopsis': '',
				'categoria': category.pk,
				'portada': uploaded_image,
			})

			self.assertRedirects(response, reverse('comics:catalogo'))
			comic = Comic.objects.get(titulo='Con portada')
			self.assertTrue(comic.portada.path.startswith(media_root))
			self.assertTrue(comic.portada.storage.exists(comic.portada.name))
			detail = self.client.get(reverse('comics:detalle_comic', args=[comic.pk]))
			self.assertContains(detail, comic.portada.url)
