from django.db import models
from django.contrib.auth.models import User

class ReporteBitacora(models.Model):
    accion = models.CharField(max_length=150)
    detalles = models.TextField()
    nivel_severidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acciones_bitacora',
    )

    def __str__(self):
        return f'{self.accion} ({self.fecha:%Y-%m-%d %H:%M})'
