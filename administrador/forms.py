from django import forms

from comics.models import Comic
from .models import ReporteBitacora


class ComicAdminForm(forms.ModelForm):
    class Meta:
        model = Comic
        fields = ['titulo', 'autor', 'anio', 'sinopsis', 'categoria', 'portada']
        labels = {
            'titulo': 'Título',
            'autor': 'Autor / Editorial',
            'anio': 'Año de publicación',
            'sinopsis': 'Sinopsis',
            'categoria': 'Categoría',
            'portada': 'Portada',
        }
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'w-full border-4 border-black p-3 font-bold'}),
            'autor': forms.TextInput(attrs={'class': 'w-full border-4 border-black p-3 font-bold'}),
            'anio': forms.NumberInput(attrs={'class': 'w-full border-4 border-black p-3 font-bold'}),
            'sinopsis': forms.Textarea(attrs={
                'class': 'w-full border-4 border-black p-3 font-bold',
                'rows': 5,
            }),
            'categoria': forms.Select(attrs={'class': 'w-full border-4 border-black p-3 font-bold'}),
            'portada': forms.ClearableFileInput(attrs={'class': 'w-full border-4 border-black p-3 font-bold'}),
        }


class ReporteBitacoraForm(forms.ModelForm):
    class Meta:
        model = ReporteBitacora
        fields = ['accion', 'detalles', 'nivel_severidad']
        labels = {
            'accion': 'Acción',
            'detalles': 'Detalles',
            'nivel_severidad': 'Nivel de severidad',
        }
        widgets = {
            'accion': forms.TextInput(attrs={'class': 'w-full border-4 border-black p-3 font-bold'}),
            'detalles': forms.Textarea(attrs={
                'class': 'w-full border-4 border-black p-3 font-bold',
                'rows': 5,
            }),
            'nivel_severidad': forms.NumberInput(attrs={
                'class': 'w-full border-4 border-black p-3 font-bold',
                'min': 1,
            }),
        }