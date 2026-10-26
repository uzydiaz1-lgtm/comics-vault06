from django import forms
from .models import ReporteBitacora


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