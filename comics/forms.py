from django import forms
from .models import CategoriaArea, Comic, UsuarioLector


class CategoriaAreaForm(forms.ModelForm):
    class Meta:
        model = CategoriaArea
        fields = ['nombre', 'descripcion']
        labels = {
            'nombre': 'Nombre del área',
            'descripcion': 'Descripción',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full border-4 border-black p-3 font-bold',
                'placeholder': 'Ej: Manga',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full border-4 border-black p-3 font-bold',
                'rows': 4,
                'placeholder': 'Describe el área',
            }),
        }


class PerfilLectorForm(forms.ModelForm):
    class Meta:
        model = UsuarioLector
        fields = ['alias', 'comic_favorito']
        labels = {
            'alias': 'Alias / Apodo',
            'comic_favorito': 'Selecciona tu Cómic Favorito',
        }
        widgets = {
            'alias': forms.TextInput(attrs={
                'class': 'w-full border-4 border-black p-3 font-bold',
                'placeholder': 'Tu alias',
            }),
            'comic_favorito': forms.Select(attrs={
                'class': 'w-full border-4 border-black p-3 font-bold',
            }),
        }


class UsuarioLectorForm(forms.ModelForm):
    class Meta:
        model = UsuarioLector
        fields = ['user', 'alias', 'comic_favorito']
        labels = {
            'user': 'Usuario',
            'alias': 'Alias / Apodo',
            'comic_favorito': 'Cómic favorito',
        }
        widgets = {
            'user': forms.Select(attrs={'class': 'w-full border-4 border-black p-3 font-bold'}),
            'alias': forms.TextInput(attrs={'class': 'w-full border-4 border-black p-3 font-bold'}),
            'comic_favorito': forms.Select(attrs={'class': 'w-full border-4 border-black p-3 font-bold'}),
        }


class ComicForm(forms.ModelForm):
    class Meta:
        model = Comic
        fields = ['titulo', 'autor', 'anio', 'sinopsis', 'categoria', 'portada']
        labels = {
            'titulo': 'Título',
            'autor': 'Autor / Editorial',
            'anio': 'Año de publicación',
            'sinopsis': 'Sinopsis',
            'categoria': 'Área',
            'portada': 'Portada',
        }
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'w-full border-4 border-black p-3 font-bold'}),
            'autor': forms.TextInput(attrs={'class': 'w-full border-4 border-black p-3 font-bold'}),
            'anio': forms.NumberInput(attrs={
                'class': 'w-full border-4 border-black p-3 font-bold',
                'min': 1,
            }),
            'sinopsis': forms.Textarea(attrs={
                'class': 'w-full border-4 border-black p-3 font-bold',
                'rows': 5,
            }),
            'categoria': forms.Select(attrs={'class': 'w-full border-4 border-black p-3 font-bold'}),
            'portada': forms.ClearableFileInput(attrs={
                'class': 'w-full border-4 border-black p-3 font-bold',
            }),
        }
