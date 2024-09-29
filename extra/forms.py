from django import forms
from .models import Destinatario, Municipio

class DestinatarioForm(forms.ModelForm):
    class Meta:
        model = Destinatario
        fields = ['nombre', 'apellidos', 'telefono', 'carnet_de_identidad',
                  'correo_electronico', 'direccion', 'municipio', 'instrucciones_entrega']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-input'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-input'}),
            'telefono': forms.TextInput(attrs={'class': 'form-input'}),
            'carnet_de_identidad': forms.TextInput(attrs={'class': 'form-input'}),
            'correo_electronico': forms.EmailInput(attrs={'class': 'form-input'}),
            'direccion': forms.TextInput(attrs={'class': 'form-input'}),
            'municipio': forms.Select(attrs={'class': 'form-input'}),
            'instrucciones_entrega': forms.Textarea(attrs={'class': 'form-input'}),
        }