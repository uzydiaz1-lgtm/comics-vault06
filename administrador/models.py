from django.db import models


class ReporteBitacora(models.Model):
	accion = models.CharField(max_length=150)
	detalles = models.TextField()
	nivel_severidad = models.IntegerField()
	fecha = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'{self.accion} ({self.fecha:%Y-%m-%d %H:%M})'
