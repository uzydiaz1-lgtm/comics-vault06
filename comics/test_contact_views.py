from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import MensajeContacto


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='contacto@example.com',
    EMAIL_HOST_USER='contacto@example.com',
)
class ContactViewsTests(TestCase):
    def test_valid_contact_submission_saves_message_sends_emails_and_redirects(self):
        response = self.client.post(reverse('comics:contacto'), {
            'nombre': 'Ada Lovelace',
            'email': 'ada@example.com',
            'mensaje': 'Quisiera más información.',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('comics:gracias'))
        self.assertEqual(MensajeContacto.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, ['contacto@example.com'])
        self.assertEqual(mail.outbox[0].reply_to, ['ada@example.com'])
        self.assertEqual(mail.outbox[1].to, ['ada@example.com'])

        thanks_page = self.client.get(response.url)
        self.assertContains(thanks_page, 'toastr.success')
        self.assertContains(thanks_page, 'cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js')
        self.assertContains(thanks_page, 'cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.js')

    def test_invalid_contact_submission_does_not_save_message(self):
        response = self.client.post(reverse('comics:contacto'), {
            'nombre': '',
            'email': 'no-es-un-correo',
            'mensaje': '',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(MensajeContacto.objects.count(), 0)
        self.assertEqual(mail.outbox, [])

    def test_message_list_requires_staff(self):
        response = self.client.get(reverse('comics:listar_mensajes'))
        self.assertRedirects(
            response,
            f"{reverse('comics:login')}?next={reverse('comics:listar_mensajes')}",
        )

        reader = User.objects.create_user(username='lector', password='password-123')
        self.client.force_login(reader)
        self.assertEqual(self.client.get(reverse('comics:listar_mensajes')).status_code, 403)

    def test_staff_can_paginate_contact_messages(self):
        staff = User.objects.create_user(
            username='staff',
            password='password-123',
            is_staff=True,
        )
        self.client.force_login(staff)
        for index in range(6):
            MensajeContacto.objects.create(
                nombre=f'Persona {index}',
                email=f'persona{index}@example.com',
                mensaje=f'Mensaje {index}',
            )

        first_page = self.client.get(reverse('comics:listar_mensajes'))
        second_page = self.client.get(reverse('comics:listar_mensajes'), {'page': 2})

        self.assertEqual(first_page.status_code, 200)
        self.assertEqual(len(first_page.context['mensajes']), 5)
        self.assertTrue(first_page.context['mensajes'].has_next())
        self.assertEqual(len(second_page.context['mensajes']), 1)
        self.assertContains(second_page, 'Página 2 de 2')
        self.assertContains(second_page, 'Consultas recibidas')
        self.assertContains(second_page, 'mailto:persona0@example.com')
