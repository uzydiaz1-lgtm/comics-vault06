from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CategoriaArea, Comic, UsuarioLector


FORM_CONTROL_CLASS = 'w-full max-w-full border-4 border-black p-3 font-bold'


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', FORM_CONTROL_CLASS)


class PerfilLectorForm(forms.ModelForm):
    class Meta:
        model = UsuarioLector
        fields = ['alias', 'telefono', 'direccion', 'ciudad', 'comic_favorito']
        labels = {
            'alias': 'Alias / Apodo',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
            'ciudad': 'Ciudad',
            'comic_favorito': 'Selecciona tu Cómic Favorito',
        }
        widgets = {
            'alias': forms.TextInput(attrs={
                'class': FORM_CONTROL_CLASS,
                'placeholder': 'Tu alias',
            }),
            'telefono': forms.TextInput(attrs={
                'class': FORM_CONTROL_CLASS,
                'autocomplete': 'tel',
            }),
            'direccion': forms.TextInput(attrs={
                'class': FORM_CONTROL_CLASS,
                'autocomplete': 'street-address',
            }),
            'ciudad': forms.TextInput(attrs={
                'class': FORM_CONTROL_CLASS,
                'autocomplete': 'address-level2',
            }),
            'comic_favorito': forms.Select(attrs={
                'class': FORM_CONTROL_CLASS,
            }),
        }


class UsuarioLectorForm(forms.ModelForm):
    class Meta:
        model = UsuarioLector
        fields = ['user', 'alias', 'telefono', 'direccion', 'ciudad', 'comic_favorito']
        labels = {
            'user': 'Usuario',
            'alias': 'Alias / Apodo',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
            'ciudad': 'Ciudad',
            'comic_favorito': 'Cómic favorito',
        }
        widgets = {
            'user': forms.Select(attrs={'class': FORM_CONTROL_CLASS}),
            'alias': forms.TextInput(attrs={'class': FORM_CONTROL_CLASS}),
            'telefono': forms.TextInput(attrs={'class': FORM_CONTROL_CLASS}),
            'direccion': forms.TextInput(attrs={'class': FORM_CONTROL_CLASS}),
            'ciudad': forms.TextInput(attrs={'class': FORM_CONTROL_CLASS}),
            'comic_favorito': forms.Select(attrs={'class': FORM_CONTROL_CLASS}),
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
            'titulo': forms.TextInput(attrs={'class': FORM_CONTROL_CLASS}),
            'autor': forms.TextInput(attrs={'class': FORM_CONTROL_CLASS}),
            'anio': forms.NumberInput(attrs={
                'class': FORM_CONTROL_CLASS,
                'min': 1,
            }),
            'sinopsis': forms.Textarea(attrs={
                'class': FORM_CONTROL_CLASS,
                'rows': 5,
            }),
            'categoria': forms.Select(attrs={'class': FORM_CONTROL_CLASS}),
            'portada': forms.ClearableFileInput(attrs={
                'class': FORM_CONTROL_CLASS,
            }),
        }

    def clean_anio(self):
        anio = self.cleaned_data['anio']
        if anio < 1:
            raise forms.ValidationError('El año debe ser mayor que cero.')
        return anio


class RegistroForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ('username',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = FORM_CONTROL_CLASS


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = FORM_CONTROL_CLASS
