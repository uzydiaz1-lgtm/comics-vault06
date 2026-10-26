from django.db import models
from django.contrib.auth.models import User

class CategoriaArea(models.Model):
    nombre = models.CharField(max_length=100)  # Ej: Cómic, Manga, Underground
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Comic(models.Model):
    titulo = models.CharField(max_length=150)
    autor = models.CharField(max_length=100)
    propietario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comics_creados',
    )
    categoria = models.ForeignKey(CategoriaArea, on_delete=models.CASCADE, related_name='comics')
    anio = models.IntegerField(default=2024)
    sinopsis = models.TextField(blank=True, null=True)
    portada = models.ImageField(upload_to='portadas/', null=True, blank=True)

    def __str__(self):
        return self.titulo

class UsuarioLector(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    alias = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    comic_favorito = models.ForeignKey(Comic, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username